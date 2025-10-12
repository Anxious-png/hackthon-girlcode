from django.shortcuts import render, redirect

# Create your views here.
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import (
    ScannedMessage, FraudReport, SuspiciousActivityLog, NumberBlacklist,
    RiskyTransaction, EducationalContent, Feedback
)

from django.utils import timezone
from .models import ScannedMessage, NumberBlacklist, FraudReport
from .forms import InvestmentForm
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse  
from .models import *
from django.contrib.auth.decorators import login_required
from .forms import SavingGoalForm
from .models import SavingGoal
from .models import BankAccount, SavingGoal
from .forms import DepositForm, AddSavingForm
from decimal import Decimal

from django.contrib.auth import logout
from django.shortcuts import redirect, render
from django.contrib import messages
from .forms import UserSignupForm, CustomLoginForm
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from .models import UserProfile
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import africastalking
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.conf import settings
from .models import ScannedMessage
from django.core.mail import send_mail
from .forms import *



def signup_view(request):
    if request.method == 'POST':
        form = UserSignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # Hash password
            user.save()
            login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect('dashboard')
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
            messages.error(request, "Invalid credentials.")
    else:
        form = CustomLoginForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    if request.method == "POST":
        logout(request)
        messages.success(request, "You have been logged out successfully.")
        return redirect("login") 
    return render(request, "logout.html")

from .models import SuspiciousActivityLog
@login_required(login_url='login')
def dashboard(request):
    messages_count = ScannedMessage.objects.filter(user=request.user).count()
    reports_count = FraudReport.objects.filter(user=request.user).count()
    alert = SuspiciousActivityLog.objects.filter(user=request.user).order_by('-timestamp').first()
    return render(request, 'dashboard.html', {
        'messages_count': messages_count,
        'reports_count': reports_count,
        'alert' : alert,
    })


def scan_message(request):
    if request.method == 'POST':
        message_text = request.POST.get('message_text', '')
        related_number = request.POST.get('related_number', None)  # optional (like sender)

        # 1. Keyword detection
        scam_keywords = [
            "free money", "pin", "unlock", "click here", "win prize", "urgent",
            "risk free", "claim", "congratulations", "you have won", "jackpot",
            "lottery", "send money", "mpesa", "airtel money", "reward", "bonus"
        ]
        detected = [kw for kw in scam_keywords if kw in message_text.lower()]
        detected_keywords_str = ', '.join(detected)
        keyword_flag = bool(detected)

        # 2. Blacklist / Reports check
        blacklist_flag = False
        report_count = 0
        if related_number:
            blacklist_flag = NumberBlacklist.objects.filter(number=related_number).exists()
            report_count = FraudReport.objects.filter(scammer_number=related_number).count()

        # 3. Final scam decision
        is_scam = keyword_flag or blacklist_flag or report_count > 0

        # Save the scanned message
        msg = ScannedMessage.objects.create(
            user=request.user if request.user.is_authenticated else None,
            message_text=message_text,
            related_number=related_number,
            is_scam=is_scam,
            detected_keywords=detected_keywords_str,
            timestamp=timezone.now(),
        )

        # Pass details to scan_result page
        return redirect('scan_result', msg_id=msg.id)

    # GET request → just show the form
    return render(request, 'scan.html')

#@login_required
def scan_result(request, msg_id):
    msg = ScannedMessage.objects.get(id=msg_id)
    return render(request, 'scan_result.html', {
        "msg": msg,
        "is_scam": msg.is_scam,
        "detected_keywords": msg.detected_keywords.split(", ") if msg.detected_keywords else [],
    })

# Report Fraud
#@login_required
def report_fraud(request):
    if request.method == 'POST':
        number = request.POST.get('scammer_number')
        message = request.POST.get('message')
        reason = request.POST.get('report_reason')

        FraudReport.objects.create(
            user=request.user,
            scammer_number=number,
            message=message,
            report_reason=reason
        )
        # Send email notification
        send_mail(
            subject="🚨 New Fraud Report Submitted",
            message=(
                f"A new fraud report has been submitted:\n\n"
                f"Reporter: {request.user.email}\n"
                f"Scammer Number: {number}\n"
                f"Message: {message}\n"
                f"Reason: {reason}\n"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=["anxious882@gmail.com"],  # change to real recipient(s)
            fail_silently=False,
        )


        # Add or update blacklist
        blacklisted, created = NumberBlacklist.objects.get_or_create(phone_number=number)
        if not created:
            blacklisted.report_count += 1
            blacklisted.save()

        messages.success(request, 'Fraud report submitted.')
        return redirect('dashboard')

    return render(request, 'report_fraud.html')

# Risky Transactions
#@login_required
def check_transaction(request):
    if request.method == 'POST':
        number = request.POST.get('receiver_number')
        amount = request.POST.get('amount')
        flagged = NumberBlacklist.objects.filter(phone_number=number).exists()

        reason = 'Blacklisted number' if flagged else ''

        RiskyTransaction.objects.create(
            user=request.user,
            receiver_number=number,
            amount=amount,
            flagged=flagged,
            reason_flagged=reason
        )

        return render(request, 'check_result.html', {'flagged': flagged, 'reason': reason})

    return render(request, 'check_transaction.html')

# Educational Content
def learn(request):
    contents = EducationalContent.objects.all()
    return render(request, 'learn.html', {'contents': contents})

# Submit Feedback
#@login_required
def submit_feedback(request):
    if request.method == 'POST':
        message = request.POST.get('message')
        Feedback.objects.create(user=request.user, message=message)
        messages.success(request, 'Thank you for your feedback!')
        return redirect('dashboard')

    return render(request, 'feedback.html')

# Suspicious Activity Log
#@login_required
"""def activity_log(request):
    logs = SuspiciousActivityLog.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, 'activity_log.html', {'logs': logs})"""


from ipware import get_client_ip
import requests

def activity_log(request, event_type, notes=""):
    ip, _ = get_client_ip(request)
    location = "Unknown"
    if ip:
        try:
            response = requests.get(f"https://ipapi.co/{ip}/json/").json()
            location = f"{response.get('city')}, {response.get('country_name')}"
        except:
            pass

    SuspiciousActivityLog.objects.create(
        user=request.user,
        event_type=event_type,
        location=location,
        notes=notes
    )



# Initialize Africa's Talking
africastalking.initialize(
    settings.AFRICASTALKING_USERNAME,
    settings.AFRICASTALKING_API_KEY
)

@csrf_exempt
def receive_sms(request):
    if request.method == "POST":
        sender = request.POST.get('from')
        message_text = request.POST.get('text')

        # Scam detection logic
        keywords = ['urgent', 'reward', 'pin', 'unlock']
        detected = [k for k in keywords if k in message_text.lower()]
        is_scam = len(detected) > 0

        # Save to DB
        ScannedMessage.objects.create(
            user=request.user if request.user.is_authenticated else None,
            message_text=message_text,
            is_scam=is_scam,
            detected_keywords=", ".join(detected),
            related_number=sender,
            scanned_at=timezone.now()
        )

        return HttpResponse("Message received", status=200)
    return HttpResponse("Invalid request", status=400)
@csrf_exempt
def incoming_sms(request):
    if request.method == 'POST':
        sender = request.POST.get('from')
        message = request.POST.get('text')
        to_number = request.POST.get('to')

        print(f"📩 New SMS from {sender} to {to_number}: {message}")

        ScannedMessage.objects.create(
            message_text=message,
            related_number=sender,
            timestamp=timezone.now(),
            is_scam=False
        )

        return HttpResponse("OK", status=200)
    return HttpResponse("Method not allowed", status=405)



@csrf_exempt
def receive_sms(request):
    if request.method == "POST":
        sender = request.POST.get('from')
        message_text = request.POST.get('text', '')

       
        scam_keywords = [
            'urgent', 'reward', 'pin', 'unlock', 'win', 'free', 'lottery',
            'claim', 'congratulations', 'bonus', 'click', 'verify', 'send money'
        ]

        
        trusted_senders = [
             'ABSA', '0800222333'
        ]

        # 🔍 3. Keyword detection
        detected = [kw for kw in scam_keywords if kw in message_text.lower()]
        is_scam = len(detected) > 0

        # 🧮 4. Confidence scoring (just a rough estimate)
        confidence_score = round((len(detected) / len(scam_keywords)) * 100, 2)

        # 🛡️ 5. If sender is trusted, mark safe regardless of keywords
        if any(name.lower() in sender.lower() for name in trusted_senders):
            is_scam = False
            confidence_score = 0

        # 💾 6. Save to database
        ScannedMessage.objects.create(
            user=request.user if request.user.is_authenticated else None,
            message_text=message_text,
            is_scam=is_scam,
            detected_keywords=", ".join(detected),
            related_number=sender,
            confidence_score=confidence_score,
            scanned_at=timezone.now()
        )

        print(f"📩 SMS from {sender}: {message_text}")
        print(f"🕵️ Detected: {detected} | Scam: {is_scam} | Confidence: {confidence_score}%")

        return HttpResponse("Message received and analyzed.", status=200)

    return HttpResponse("Invalid request", status=400)

def lock_account(request):
    # Example: deactivate user account
    request.user.is_active = False
    request.user.save()

    messages.error(request, " Your account has been locked for security. Contact support to unlock.")
    return redirect("dashboard")


def confirm_login(request):
    # Example: record confirmation
    # (You could also log it in an ActivityLog model)
    messages.success(request, f" Login confirmed at {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return redirect("dashboard")

def spending_summary(request):
    transactions = Transaction.objects.filter(user=request.user)
    summary = (
        transactions.values("category")
        .annotate(total=Sum("amount"))
        .order_by("-total")
    )

    return render(request, "spending_summary.html", {"summary": summary})


def check_transaction_risk(request):
    if request.method == "POST":
        receiver_number = request.POST.get("receiver_number")
        amount = float(request.POST.get("amount", 0))

        # Risk logic
        high_amount_threshold = 500000  
        flagged_numbers = ["+256700123456", "+256772000111"]

        is_high = amount > high_amount_threshold
        is_flagged = receiver_number in flagged_numbers

        if is_high or is_flagged:
            risk_level = "High"
        else:
            risk_level = "Low"

        return render(request, "transaction_risk.html", {
            "risk_level": risk_level,
            "receiver_number": receiver_number,
            "amount": amount
        })

    return render(request, "check_transaction.html")

@login_required
def savings_dashboard(request):
    # 1️⃣ Get or create user's bank account
    account, _ = BankAccount.objects.get_or_create(user=request.user, defaults={"balance": 5000000.00})  # Default 5M balance

    # 2️⃣ Get the user's latest saving goal
    goal = SavingGoal.objects.filter(user=request.user).last()

    # 3️⃣ If user is submitting a saving amount
    if request.method == "POST":
        save_amount = float(request.POST.get("amount", 0))
        if save_amount <= 0:
            messages.error(request, "Please enter a valid saving amount.")
            return redirect("savings_dashboard")

        if save_amount > account.balance:
            messages.error(request, "Insufficient funds in your account.")
            return redirect("savings_dashboard")

        # Deduct from bank account
        account.balance -= save_amount
        account.save()

        # Add to existing saving goal
        if goal:
            goal.current_savings += save_amount
            goal.save()
        else:
            messages.error(request, "No saving goal set yet.")
            return redirect("savings_dashboard")

        messages.success(request, f"UGX {save_amount:,.0f} saved successfully!")

        return redirect("savings_dashboard")

    # 4️⃣ AI Feedback messages
    ai_feedback = None
    if goal:
        progress = goal.progress_percent
        if progress == 0:
            ai_feedback = "You haven’t started yet. Let’s make your first save!"
        elif progress < 25:
            ai_feedback = f"Good start! You’ve saved {progress}% of your goal."
        elif progress < 50:
            ai_feedback = f"Keep it up! {progress}% saved — you’re halfway there."
        elif progress < 75:
            ai_feedback = f"Almost there! {progress}% saved. Great consistency!"
        elif progress < 100:
            ai_feedback = f"Incredible! {progress}% saved — so close to your goal!"
        else:
            ai_feedback = "🎉 You’ve achieved your goal! Time to grow your savings further."

   
    investment_suggestions = []
    if goal and goal.progress_percent >= 50:
        investment_suggestions = InvestmentOption.objects.all()[:3]

    
    return render(request, "savings_dashboard.html", {
        "account": account,
        "goal": goal,
        "ai_feedback": ai_feedback,
        "investment_suggestions": investment_suggestions,
    })
@login_required
def transfer_to_savings(request):
    account = BankAccount.objects.get(user=request.user)
    goal = SavingGoal.objects.filter(user=request.user).last()

    if request.method == "POST":
        amount = float(request.POST.get("amount", 0))

        if amount <= 0:
            messages.error(request, "Please enter a valid amount.")
        elif amount > float(account.balance):
            messages.error(request, "Insufficient balance.")
        elif not goal:
            messages.error(request, "You have no active savings goal.")
        else:
            # Deduct from bank account
            account.balance -= amount
            account.save()

            # Add to savings
            goal.current_savings += amount
            goal.save()

            messages.success(request, f" UGX {amount} saved successfully!")

            return redirect("savings_dashboard")

    return render(request, "transfer_to_savings.html", {"account": account, "goal": goal})

@login_required
def deposit_money(request):
    account, _ = BankAccount.objects.get_or_create(user=request.user, defaults={"balance": 5000000.00})  # Default 5M balance
    if request.method == "POST":
        form = DepositForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data["amount"]
            account.deposit(amount)
            messages.success(request, f"UGX {amount} deposited successfully!")
            if amount <= 0:
                messages.error(request, "Please enter a valid amount.")
                return redirect("deposit_money")
            return redirect("savings_dashboard")
    else:
        form = DepositForm()
    return render(request, "deposit.html", {"form": form, "account": account})


@login_required
def add_savings(request):
    account, _ = BankAccount.objects.get_or_create(user=request.user)
    goal = SavingGoal.objects.filter(user=request.user).last()

    if not goal:
        messages.error(request, "You must first create a saving goal!")
        return redirect("savings_dashboard")

    if request.method == "POST":
        form = AddSavingForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data["amount"]
            if amount <= account.balance:
                account.withdraw(amount)  
                goal.current_savings += amount  
                goal.save()
                messages.success(request, f"UGX {amount} added to your savings goal!")
            else:
                messages.error(request, "Insufficient balance in your account.")
            return redirect("savings_dashboard")
    else:
        form = AddSavingForm()
    return render(request, "add_savings.html", {"form": form, "account": account, "goal": goal})


@login_required
def set_saving_goal(request):
    if request.method == 'POST':
        form = SavingGoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            return redirect('savings_dashboard')
    else:
        form = SavingGoalForm()

    return render(request, 'set_saving_goal.html', {'form': form})




@login_required
def withdraw_money(request):
    account = BankAccount.objects.get(user=request.user)
    if request.method == "POST":
        form = WithdrawForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data["amount"]

            if amount > account.balance:
                messages.error(request, "Insufficient funds!")
                return redirect("withdraw_money")

            account.withdraw(amount)

            Transaction.objects.create(
                    user=request.user,
                    amount=amount,
                    category="withdrawal",  # ✅ updated field name
                    description="User withdrawal from bank account"
                )


            # Spending alert logic
            """check_spending_alerts(request.user, account)"""

            messages.success(request, f"UGX {amount:,.0f} withdrawn successfully!")
            return redirect("savings_dashboard")
    else:
        form = WithdrawForm()
    return render(request, "withdraw.html", {"form": form})



"""def check_spending_alerts(user, account):
    # Get this month's total withdrawals and purchases
    start_of_month = timezone.now().replace(day=1)
    total_spent = Transaction.objects.filter(
        user=user,
        transaction_type__in=['withdrawal', 'purchase'],
        timestamp__gte=start_of_month
    ).aggregate(total=models.Sum('amount'))['total'] or 0

    # Get saving goal if any
    goal = SavingGoal.objects.filter(user=user).last()

    # Trigger overspending alerts
    if total_spent > (account.balance * Decimal(0.8)):
        SpendingAlert.objects.create(user=user, message="⚠️ You’ve spent over 80% of your balance this month!")

    if goal and goal.goal_amount > 0 and goal.current_savings < (goal.goal_amount * Decimal(0.3)) and total_spent > 1000000:
        SpendingAlert.objects.create(user=user, message="💡 You’re spending a lot but haven’t saved much toward your goal yet.")"""


@login_required
def transaction_history(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, "transactions.html", {"transactions": transactions})




@login_required
def invest(request):
    account, _ = BankAccount.objects.get_or_create(user=request.user, defaults={'balance': 0})
    if request.method == 'POST':
        form = InvestmentForm(request.POST)
        if form.is_valid():
            investment = form.save(commit=False)
            investment.user = request.user

            if account.balance >= investment.min_amount:
                account.balance -= investment.min_amount
                account.save()
                investment.save()
                messages.success(request, f"You’ve successfully invested UGX {investment.min_amount}!")
                return redirect('savings_dashboard')
            else:
                messages.error(request, "Insufficient balance for this investment.")
    else:
        form = InvestmentForm()

    return render(request, 'investments.html', {'form': form, 'account': account})

    