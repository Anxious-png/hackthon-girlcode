from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum, Count
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from decimal import Decimal
import requests

from .models import (
    UserProfile, BankAccount, Transaction, SavingGoal,
    ScannedMessage, FraudReport, NumberBlacklist, RiskyTransaction,
    SuspiciousActivityLog, EducationalContent, Feedback, InvestmentOption,
)
from .forms import (
    UserSignupForm, CustomLoginForm, SavingGoalForm,
    DepositForm, AddSavingForm, WithdrawForm, InvestmentForm,
    SetPinForm, PinVerifyForm,
)
from .ml_scanner import analyze_message
import africastalking


# ─────────────────────────────────────────────────────────────────────────────
# PIN HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _pin_guard(request):
    """
    Returns (blocked, response):
      - If user has no PIN set → redirect to set_pin
      - If PIN is locked → redirect to pin_locked
      - Otherwise → (False, None)
    """
    user = request.user
    if not user.pin_set:
        messages.warning(request, "Please set your transaction PIN before making transactions.")
        return True, redirect('set_pin')
    if user.pin_locked:
        return True, redirect('pin_locked')
    return False, None


def _verify_pin_and_proceed(request, action_label, icon, amount, description,
                             recipient, cancel_url, execute_fn):
    """
    Two-phase confirmation flow:
      Phase 1 (GET or first POST): show confirm_transaction.html
      Phase 2 (POST with confirmed=1 + pin): verify PIN → run execute_fn()
    """
    user = request.user
    account = BankAccount.objects.filter(user=user).first()
    balance_after = (account.balance - Decimal(str(amount))) if account else Decimal('0')

    # Collect original form data to pass through hidden fields
    form_data = {k: v for k, v in request.POST.items()
                 if k not in ('csrfmiddlewaretoken', 'confirmed', 'pin')}

    if request.method == 'POST' and request.POST.get('confirmed') == '1':
        raw_pin = request.POST.get('pin', '')
        if user.verify_transaction_pin(raw_pin):
            return execute_fn()
        else:
            attempts_left = max(0, 3 - user.pin_attempts)
            pin_error = "Incorrect PIN. Please try again." if not user.pin_locked else None
            if user.pin_locked:
                return redirect('pin_locked')
            return render(request, 'confirm_transaction.html', {
                'action_label': action_label, 'icon': icon,
                'amount': amount, 'description': description,
                'recipient': recipient, 'cancel_url': cancel_url,
                'balance_after': balance_after, 'form_data': form_data,
                'pin_error': pin_error, 'attempts_left': attempts_left,
            })

    return render(request, 'confirm_transaction.html', {
        'action_label': action_label, 'icon': icon,
        'amount': amount, 'description': description,
        'recipient': recipient, 'cancel_url': cancel_url,
        'balance_after': balance_after, 'form_data': form_data,
    })


# ─────────────────────────────────────────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────────────────────────────────────────

def signup_view(request):
    if request.method == 'POST':
        form = UserSignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            # Set transaction PIN from signup form
            user.set_transaction_pin(form.cleaned_data['transaction_pin'])
            BankAccount.objects.get_or_create(user=user, defaults={"balance": Decimal("5000000.00")})
            login(request, user)
            messages.success(request, "Account created! Welcome to SilentGuard.")
            return redirect('savings_dashboard')
    else:
        form = UserSignupForm()
    return render(request, 'signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('savings_dashboard')
        else:
            messages.error(request, "Invalid credentials. Please try again.")
    else:
        form = CustomLoginForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    if request.method == "POST":
        logout(request)
        messages.success(request, "Logged out successfully.")
        return redirect("login")
    return render(request, "logout.html")


# ─────────────────────────────────────────────────────────────────────────────
# PIN MANAGEMENT
# ─────────────────────────────────────────────────────────────────────────────

@login_required(login_url='login')
def set_pin(request):
    """Set or change transaction PIN."""
    is_change = request.user.pin_set
    form = SetPinForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        request.user.set_transaction_pin(form.cleaned_data['new_pin'])
        messages.success(request, "Transaction PIN set successfully!")
        return redirect('savings_dashboard')
    return render(request, 'set_pin.html', {'form': form, 'is_change': is_change})


@login_required(login_url='login')
def pin_locked(request):
    """Shown when PIN is locked after 3 failed attempts."""
    return render(request, 'pin_locked.html')


@login_required(login_url='login')
def unlock_pin(request):
    """Admin/support action to unlock a user's PIN (via admin or support flow)."""
    # Only superusers can unlock via URL; regular users go through support
    if request.user.is_superuser:
        username = request.GET.get('user')
        if username:
            try:
                target = UserProfile.objects.get(username=username)
                target.pin_locked = False
                target.pin_attempts = 0
                target.save(update_fields=['pin_locked', 'pin_attempts'])
                messages.success(request, f"PIN unlocked for {username}.")
            except UserProfile.DoesNotExist:
                messages.error(request, "User not found.")
    return redirect('dashboard')


# ─────────────────────────────────────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────

@login_required(login_url='login')
def dashboard(request):
    messages_count = ScannedMessage.objects.filter(user=request.user).count()
    scam_count = ScannedMessage.objects.filter(user=request.user, is_scam=True).count()
    reports_count = FraudReport.objects.filter(user=request.user).count()
    alert = SuspiciousActivityLog.objects.filter(user=request.user).order_by('-timestamp').first()
    recent_scans = ScannedMessage.objects.filter(user=request.user).order_by('-scanned_at')[:5]

    return render(request, 'dashboard.html', {
        'messages_count': messages_count,
        'scam_count': scam_count,
        'reports_count': reports_count,
        'alert': alert,
        'recent_scans': recent_scans,
        'suspicious_count': scam_count,
    })


# ─────────────────────────────────────────────────────────────────────────────
# FRAUD DETECTION
# ─────────────────────────────────────────────────────────────────────────────

@login_required(login_url='login')
def scan_message(request):
    if request.method == 'POST':
        message_text = request.POST.get('message_text', '').strip()
        related_number = request.POST.get('related_number', '').strip() or None

        if not message_text:
            messages.error(request, "Please enter a message to scan.")
            return redirect('scan_message')

        result = analyze_message(message_text, sender=related_number or "")

        # Blacklist check on top of ML
        if related_number:
            bl = NumberBlacklist.objects.filter(phone_number=related_number).first()
            if bl:
                result['is_scam'] = True
                result['confidence_score'] = max(result['confidence_score'], 85.0)
                result['risk_level'] = 'High'
                if 'blacklisted number' not in result['detected_keywords']:
                    result['detected_keywords'].append('blacklisted number')

        msg = ScannedMessage.objects.create(
            user=request.user,
            message_text=message_text,
            related_number=related_number,
            is_scam=result['is_scam'],
            detected_keywords=', '.join(result['detected_keywords']),
            confidence_score=result['confidence_score'],
            timestamp=timezone.now(),
        )
        return redirect('scan_result', msg_id=msg.id)

    return render(request, 'scan.html')


@login_required(login_url='login')
def scan_result(request, msg_id):
    msg = get_object_or_404(ScannedMessage, id=msg_id, user=request.user)
    keywords = [k.strip() for k in msg.detected_keywords.split(',') if k.strip()] if msg.detected_keywords else []

    score = msg.confidence_score or 0
    if score >= 70:
        risk_level, risk_color = "High", "danger"
    elif score >= 40:
        risk_level, risk_color = "Medium", "warning"
    elif score >= 20:
        risk_level, risk_color = "Low", "info"
    else:
        risk_level, risk_color = "Safe", "success"

    return render(request, 'scan_result.html', {
        "msg": msg,
        "is_scam": msg.is_scam,
        "detected_keywords": keywords,
        "risk_level": risk_level,
        "risk_color": risk_color,
    })


@login_required(login_url='login')
def report_fraud(request):
    if request.method == 'POST':
        number = request.POST.get('scammer_number', '').strip()
        message = request.POST.get('message', '').strip()
        reason = request.POST.get('report_reason', '').strip()

        if not number or not message:
            messages.error(request, "Please fill in all required fields.")
            return render(request, 'report_fraud.html')

        FraudReport.objects.create(user=request.user, scammer_number=number, message=message, report_reason=reason)

        blacklisted, created = NumberBlacklist.objects.get_or_create(
            phone_number=number, defaults={"added_by": request.user}
        )
        if not created:
            blacklisted.report_count += 1
            blacklisted.save()

        try:
            send_mail(
                subject="New Fraud Report — SilentGuard",
                message=f"Reporter: {request.user.username}\nNumber: {number}\nMessage: {message}\nReason: {reason}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.DEFAULT_FROM_EMAIL],
                fail_silently=True,
            )
        except Exception:
            pass

        messages.success(request, f"Report submitted. {number} has been flagged.")
        return redirect('dashboard')

    return render(request, 'report_fraud.html')


@login_required(login_url='login')
def check_transaction(request):
    if request.method == 'POST':
        number = request.POST.get('receiver_number', '').strip()
        try:
            amount = float(request.POST.get('amount', '0'))
        except ValueError:
            amount = 0

        bl = NumberBlacklist.objects.filter(phone_number=number).first()
        flagged = bl is not None
        report_count = bl.report_count if bl else 0
        high_amount = amount > 500000

        reason = ""
        if flagged:
            reason += f"This number has been reported {report_count} time(s) for fraud. "
        if high_amount:
            reason += "High-value transaction — verify the recipient carefully."

        RiskyTransaction.objects.create(
            user=request.user, receiver_number=number, amount=amount,
            flagged=flagged or high_amount, reason_flagged=reason,
        )

        return render(request, 'check_result.html', {
            'flagged': flagged or high_amount,
            'reason': reason,
            'number': number,
            'amount': amount,
            'report_count': report_count,
            'high_amount': high_amount,
        })

    return render(request, 'check_transaction.html')


# ─────────────────────────────────────────────────────────────────────────────
# SECURITY
# ─────────────────────────────────────────────────────────────────────────────

@login_required(login_url='login')
def lock_account(request):
    user = request.user
    user.set_unusable_password()
    user.save()
    logout(request)
    messages.warning(request, "Account locked. Contact support to regain access.")
    return redirect("login")


@login_required(login_url='login')
def confirm_login(request):
    SuspiciousActivityLog.objects.filter(user=request.user).update(notes="Confirmed by user")
    messages.success(request, f"Login confirmed at {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return redirect("dashboard")


@login_required(login_url='login')
def activity_log(request):
    logs = SuspiciousActivityLog.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, 'activity_log.html', {'logs': logs})


def _log_suspicious_activity(request, event_type, notes=""):
    try:
        from ipware import get_client_ip
        ip, _ = get_client_ip(request)
        location = "Unknown"
        if ip:
            resp = requests.get(f"https://ipapi.co/{ip}/json/", timeout=3).json()
            location = f"{resp.get('city', '')}, {resp.get('country_name', '')}".strip(", ")
    except Exception:
        location = "Unknown"
    SuspiciousActivityLog.objects.create(user=request.user, event_type=event_type, location=location, notes=notes)


# ─────────────────────────────────────────────────────────────────────────────
# FINANCIAL
# ─────────────────────────────────────────────────────────────────────────────

@login_required(login_url='login')
def savings_dashboard(request):
    account, _ = BankAccount.objects.get_or_create(
        user=request.user, defaults={"balance": Decimal("5000000.00")}
    )
    goal = SavingGoal.objects.filter(user=request.user).last()

    ai_feedback = None
    if goal:
        p = goal.progress_percent
        if p == 0:
            ai_feedback = "You haven't started yet. Make your first save today!"
        elif p < 25:
            ai_feedback = f"Good start! You've saved {p}% of your goal. Keep going!"
        elif p < 50:
            ai_feedback = f"You're at {p}% — halfway there. Stay consistent!"
        elif p < 75:
            ai_feedback = f"Amazing! {p}% saved. You're in the home stretch."
        elif p < 100:
            ai_feedback = f"So close! {p}% saved — just a little more to go!"
        else:
            ai_feedback = "Goal achieved! Time to invest and grow your wealth."

    investment_suggestions = []
    if goal and goal.progress_percent >= 50:
        investment_suggestions = InvestmentOption.objects.all()[:3]

    spending = (
        Transaction.objects.filter(user=request.user)
        .values('category').annotate(total=Sum('amount')).order_by('-total')
    )
    chart_labels = [s['category'] for s in spending]
    chart_data = [float(s['total']) for s in spending]

    return render(request, 'savings_dashboard.html', {
        "account": account,
        "goal": goal,
        "ai_feedback": ai_feedback,
        "investment_suggestions": investment_suggestions,
        "chart_labels": chart_labels,
        "chart_data": chart_data,
    })


@login_required(login_url='login')
def set_saving_goal(request):
    existing = SavingGoal.objects.filter(user=request.user).last()
    if request.method == 'POST':
        form = SavingGoalForm(request.POST, instance=existing)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            messages.success(request, "Savings goal saved!")
            return redirect('savings_dashboard')
    else:
        form = SavingGoalForm(instance=existing)
    return render(request, 'set_saving_goal.html', {'form': form, 'existing': existing})


@login_required(login_url='login')
def deposit_money(request):
    blocked, resp = _pin_guard(request)
    if blocked:
        return resp

    account, _ = BankAccount.objects.get_or_create(
        user=request.user, defaults={"balance": Decimal("5000000.00")}
    )

    # Phase 1: show deposit form
    if request.method == 'GET' or (request.method == 'POST' and request.POST.get('confirmed') != '1'):
        form = DepositForm(request.POST or None)
        if request.method == 'POST' and form.is_valid():
            amount = form.cleaned_data['amount']
            description = form.cleaned_data.get('description') or 'Bank deposit'
            # Go to confirmation screen
            return _verify_pin_and_proceed(
                request,
                action_label='Deposit',
                icon='💰',
                amount=amount,
                description=description,
                recipient=None,
                cancel_url='/deposit/',
                execute_fn=lambda: _do_deposit(request, account, amount, description),
            )
        return render(request, 'deposit.html', {'form': form, 'account': account})

    # Phase 2: PIN confirmed — execute
    try:
        amount = Decimal(request.POST.get('amount', '0'))
        description = request.POST.get('description') or 'Bank deposit'
    except Exception:
        messages.error(request, "Invalid amount.")
        return redirect('deposit_money')

    return _verify_pin_and_proceed(
        request,
        action_label='Deposit',
        icon='💰',
        amount=amount,
        description=description,
        recipient=None,
        cancel_url='/deposit/',
        execute_fn=lambda: _do_deposit(request, account, amount, description),
    )


def _do_deposit(request, account, amount, description):
    account.deposit(amount)
    Transaction.objects.create(
        user=request.user, amount=amount, category="Deposit", description=description
    )
    messages.success(request, f"✅ UGX {amount:,.0f} deposited successfully!")
    return redirect('savings_dashboard')


@login_required(login_url='login')
def add_savings(request):
    blocked, resp = _pin_guard(request)
    if blocked:
        return resp

    account, _ = BankAccount.objects.get_or_create(user=request.user)
    goal = SavingGoal.objects.filter(user=request.user).last()

    if not goal:
        messages.error(request, "Create a savings goal first!")
        return redirect("set_savings_goal")

    if request.method == 'GET' or (request.method == 'POST' and request.POST.get('confirmed') != '1'):
        form = AddSavingForm(request.POST or None)
        if request.method == 'POST' and form.is_valid():
            amount = form.cleaned_data['amount']
            if amount > account.balance:
                messages.error(request, "Insufficient balance.")
                return render(request, 'add_savings.html', {'form': form, 'account': account, 'goal': goal})
            return _verify_pin_and_proceed(
                request,
                action_label='Save to Goal',
                icon='🏦',
                amount=amount,
                description=f"Transfer to: {goal.goal_name}",
                recipient=goal.goal_name,
                cancel_url='/add-savings/',
                execute_fn=lambda: _do_add_savings(request, account, goal, amount),
            )
        return render(request, 'add_savings.html', {'form': form, 'account': account, 'goal': goal})

    try:
        amount = Decimal(request.POST.get('amount', '0'))
    except Exception:
        messages.error(request, "Invalid amount.")
        return redirect('add_savings')

    return _verify_pin_and_proceed(
        request,
        action_label='Save to Goal',
        icon='🏦',
        amount=amount,
        description=f"Transfer to: {goal.goal_name}",
        recipient=goal.goal_name,
        cancel_url='/add-savings/',
        execute_fn=lambda: _do_add_savings(request, account, goal, amount),
    )


def _do_add_savings(request, account, goal, amount):
    account.withdraw(amount)
    goal.current_savings += amount
    goal.save()
    Transaction.objects.create(
        user=request.user, amount=amount, category="Transfer",
        description=f"Transfer to savings: {goal.goal_name}",
    )
    messages.success(request, f"✅ UGX {amount:,.0f} added to your savings goal!")
    return redirect('savings_dashboard')


@login_required(login_url='login')
def transfer_to_savings(request):
    blocked, resp = _pin_guard(request)
    if blocked:
        return resp

    account = get_object_or_404(BankAccount, user=request.user)
    goal = SavingGoal.objects.filter(user=request.user).last()

    if request.method == 'GET' or (request.method == 'POST' and request.POST.get('confirmed') != '1'):
        if request.method == 'POST':
            try:
                amount = Decimal(request.POST.get('amount', '0'))
            except Exception:
                amount = Decimal('0')
            if amount <= 0:
                messages.error(request, "Enter a valid amount.")
            elif amount > account.balance:
                messages.error(request, "Insufficient balance.")
            elif not goal:
                messages.error(request, "No active savings goal.")
            else:
                return _verify_pin_and_proceed(
                    request,
                    action_label='Transfer to Savings',
                    icon='🏦',
                    amount=amount,
                    description=f"Savings goal: {goal.goal_name}",
                    recipient=goal.goal_name,
                    cancel_url='/transfer-to-savings/',
                    execute_fn=lambda: _do_transfer_savings(request, account, goal, amount),
                )
        return render(request, 'transfer_to_savings.html', {'account': account, 'goal': goal})

    try:
        amount = Decimal(request.POST.get('amount', '0'))
    except Exception:
        messages.error(request, "Invalid amount.")
        return redirect('transfer_to_savings')

    return _verify_pin_and_proceed(
        request,
        action_label='Transfer to Savings',
        icon='🏦',
        amount=amount,
        description=f"Savings goal: {goal.goal_name if goal else ''}",
        recipient=goal.goal_name if goal else '',
        cancel_url='/transfer-to-savings/',
        execute_fn=lambda: _do_transfer_savings(request, account, goal, amount),
    )


def _do_transfer_savings(request, account, goal, amount):
    account.balance -= amount
    account.save()
    goal.current_savings += amount
    goal.save()
    Transaction.objects.create(
        user=request.user, amount=amount, category="Transfer",
        description=f"Transfer to savings: {goal.goal_name}",
    )
    messages.success(request, f"✅ UGX {amount:,.0f} transferred to savings!")
    return redirect('savings_dashboard')


@login_required(login_url='login')
def withdraw_money(request):
    blocked, resp = _pin_guard(request)
    if blocked:
        return resp

    account = get_object_or_404(BankAccount, user=request.user)

    if request.method == 'GET' or (request.method == 'POST' and request.POST.get('confirmed') != '1'):
        form = WithdrawForm(request.POST or None)
        if request.method == 'POST' and form.is_valid():
            amount = form.cleaned_data['amount']
            reason = form.cleaned_data.get('reason') or 'Withdrawal'
            if amount > account.balance:
                messages.error(request, "Insufficient funds!")
                return render(request, 'withdraw.html', {'form': form, 'account': account})
            return _verify_pin_and_proceed(
                request,
                action_label='Withdrawal',
                icon='💸',
                amount=amount,
                description=reason,
                recipient=None,
                cancel_url='/withdraw/',
                execute_fn=lambda: _do_withdraw(request, account, amount, reason),
            )
        return render(request, 'withdraw.html', {'form': form, 'account': account})

    try:
        amount = Decimal(request.POST.get('amount', '0'))
        reason = request.POST.get('reason') or 'Withdrawal'
    except Exception:
        messages.error(request, "Invalid amount.")
        return redirect('withdraw_money')

    return _verify_pin_and_proceed(
        request,
        action_label='Withdrawal',
        icon='💸',
        amount=amount,
        description=reason,
        recipient=None,
        cancel_url='/withdraw/',
        execute_fn=lambda: _do_withdraw(request, account, amount, reason),
    )


def _do_withdraw(request, account, amount, reason):
    try:
        account.withdraw(amount)
    except ValueError as e:
        messages.error(request, str(e))
        return redirect('withdraw_money')
    Transaction.objects.create(
        user=request.user, amount=amount, category="Withdrawal", description=reason
    )
    messages.success(request, f"✅ UGX {amount:,.0f} withdrawn successfully!")
    return redirect('savings_dashboard')


@login_required(login_url='login')
def transaction_history(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-timestamp')
    total_in = transactions.filter(category="Deposit").aggregate(t=Sum('amount'))['t'] or 0
    total_out = transactions.filter(category__in=["Withdrawal", "Transfer"]).aggregate(t=Sum('amount'))['t'] or 0
    breakdown = (
        transactions.values('category')
        .annotate(total=Sum('amount'), count=Count('id'))
        .order_by('-total')
    )
    return render(request, "transactions.html", {
        "transactions": transactions,
        "total_in": total_in,
        "total_out": total_out,
        "breakdown": breakdown,
    })


@login_required(login_url='login')
def spending_summary(request):
    transactions = Transaction.objects.filter(user=request.user)
    summary = transactions.values("category").annotate(total=Sum("amount")).order_by("-total")
    return render(request, "spending_summary.html", {"summary": summary})


# ─────────────────────────────────────────────────────────────────────────────
# INVESTMENTS
# ─────────────────────────────────────────────────────────────────────────────

@login_required(login_url='login')
def invest(request):
    account, _ = BankAccount.objects.get_or_create(user=request.user, defaults={'balance': 0})
    options = InvestmentOption.objects.all()

    if request.method == 'POST':
        investment_id = request.POST.get('investment_id')
        try:
            option = InvestmentOption.objects.get(id=investment_id)
        except InvestmentOption.DoesNotExist:
            messages.error(request, "Investment option not found.")
            return redirect('investment_options')

        if account.balance < option.min_amount:
            messages.error(request, f"Insufficient balance. You need at least UGX {option.min_amount:,.0f}.")
            return redirect('investment_options')

        # Deduct minimum amount and record transaction
        account.withdraw(option.min_amount)
        Transaction.objects.create(
            user=request.user,
            amount=option.min_amount,
            category="Other",
            description=f"Investment: {option.name} ({option.category})",
        )
        messages.success(request, f"✅ You've successfully invested UGX {option.min_amount:,.0f} in {option.name}!")
        return redirect('savings_dashboard')

    return render(request, 'investments.html', {'options': options, 'account': account})


# ─────────────────────────────────────────────────────────────────────────────
# PROFILE
# ─────────────────────────────────────────────────────────────────────────────

@login_required(login_url='login')
def profile_view(request):
    account = BankAccount.objects.filter(user=request.user).first()
    scans_total = ScannedMessage.objects.filter(user=request.user).count()
    scams_caught = ScannedMessage.objects.filter(user=request.user, is_scam=True).count()
    reports_made = FraudReport.objects.filter(user=request.user).count()

    if request.method == "POST":
        user = request.user
        user.email = request.POST.get("email", user.email)
        user.phonenumber = request.POST.get("phonenumber", user.phonenumber)
        user.location = request.POST.get("location", user.location)
        user.save()
        messages.success(request, "Profile updated successfully!")
        return redirect("profile")

    return render(request, 'profile.html', {
        "account": account,
        "scans_total": scans_total,
        "scams_caught": scams_caught,
        "reports_made": reports_made,
    })


# ─────────────────────────────────────────────────────────────────────────────
# EDUCATION & FEEDBACK
# ─────────────────────────────────────────────────────────────────────────────

def learn(request):
    contents = EducationalContent.objects.all()
    return render(request, 'learn.html', {'contents': contents})


def learn_detail(request, pk):
    article = get_object_or_404(EducationalContent, pk=pk)
    related = EducationalContent.objects.filter(category=article.category).exclude(pk=pk)[:3]
    return render(request, 'learn_detail.html', {'article': article, 'related': related})


@login_required(login_url='login')
def submit_feedback(request):
    if request.method == 'POST':
        message = request.POST.get('message', '').strip()
        if message:
            Feedback.objects.create(user=request.user, message=message)
            messages.success(request, 'Thank you for your feedback!')
        return redirect('dashboard')
    return render(request, 'feedback.html')


# ─────────────────────────────────────────────────────────────────────────────
# SMS WEBHOOKS (Africa's Talking)
# ─────────────────────────────────────────────────────────────────────────────

try:
    africastalking.initialize(settings.AFRICASTALKING_USERNAME, settings.AFRICASTALKING_API_KEY)
except Exception:
    pass


@csrf_exempt
def receive_sms(request):
    if request.method != "POST":
        return HttpResponse("Invalid request", status=400)

    sender = request.POST.get('from', '')
    message_text = request.POST.get('text', '')

    result = analyze_message(message_text, sender=sender)

    ScannedMessage.objects.create(
        user=None,
        message_text=message_text,
        is_scam=result['is_scam'],
        detected_keywords=', '.join(result['detected_keywords']),
        related_number=sender,
        confidence_score=result['confidence_score'],
        timestamp=timezone.now(),
    )
    return HttpResponse("OK", status=200)


@csrf_exempt
def incoming_sms(request):
    if request.method != 'POST':
        return HttpResponse("Method not allowed", status=405)

    sender = request.POST.get('from', '')
    message = request.POST.get('text', '')

    result = analyze_message(message, sender=sender)
    ScannedMessage.objects.create(
        message_text=message,
        related_number=sender,
        timestamp=timezone.now(),
        is_scam=result['is_scam'],
        confidence_score=result['confidence_score'],
        detected_keywords=', '.join(result['detected_keywords']),
    )
    return HttpResponse("OK", status=200)
