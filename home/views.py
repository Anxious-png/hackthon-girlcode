from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import (
    ScannedMessage, FraudReport, SuspiciousActivityLog, NumberBlacklist,
    RiskyTransaction, EducationalContent, Feedback
)
from django.utils import timezone
from .forms import UserSignupForm, CustomLoginForm
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import UserProfile
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import africastalking
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.conf import settings
from .models import ScannedMessage


# Dashboard
#@login_required

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
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid credentials.")
    else:
        form = CustomLoginForm()
    return render(request, 'login.html', {'form': form})

#@login_required(login_url='login')
def dashboard(request):
    messages_count = ScannedMessage.objects.filter(user=request.user).count()
    reports_count = FraudReport.objects.filter(user=request.user).count()
    return render(request, 'dashboard.html', {
        'messages_count': messages_count,
        'reports_count': reports_count,
    })

# Scan Message
"""@login_required
def scan_message(request):
    if request.method == 'POST':
        text = request.POST.get('message_text')
        keywords = ['urgent', 'reward', 'pin', 'unlock',]
        detected = [k for k in keywords if k in text.lower()]
        is_scam = len(detected) > 0

        msg = ScannedMessage.objects.create(
            user=request.user,
            message_text=text,
            is_scam=is_scam,
            detected_keywords=", ".join(detected)
        )
        messages.success(request, 'Message scanned successfully.')
        return redirect('scan_result', msg.id)

    return render(request, 'scan.html')
"""

def scan_message(request):
    if request.method == 'POST':
        message_text = request.POST.get('message_text', '')
        scam_keywords = ['free money','pin','unlock', 'click here', 'win prize', 'urgent', 'risk free']  # expand as needed
        
        # Find which keywords appear in the message (case-insensitive)
        detected = [kw for kw in scam_keywords if kw in message_text.lower()]
        
        is_scam = bool(detected)
        detected_keywords_str = ', '.join(detected)
        
        # Create and save the scanned message
        msg = ScannedMessage.objects.create(
            user=request.user,
            message_text=message_text,
            is_scam=is_scam,
            detected_keywords=detected_keywords_str
        )
        
        # Redirect or render scan_result with the message id
        return redirect('scan_result', msg_id=msg.id)
    
    # If GET request, just render scanning form
    return render(request, 'scan.html')








#@login_required
def scan_result(request, msg_id):
    msg = get_object_or_404(ScannedMessage, id=msg_id, user=request.user)
    return render(request, 'scan_result.html', {'msg': msg})

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

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json

@csrf_exempt  # Africa's Talking won't send CSRF tokens
def incoming_sms(request):
    if request.method == 'POST':
        # Africa's Talking sends form-encoded data
        sender = request.POST.get('from')
        message = request.POST.get('text')
        to_number = request.POST.get('to')

        print(f"📩 New SMS from {sender} to {to_number}: {message}")

    # Save to DB
        ScannedMessage.objects.create(
            message_text=message,
            related_number=sender,
            timestamp=timezone.now(),
            is_scam=False  # Run detection later
        )

        return HttpResponse("OK", status=200)

    return HttpResponse("Method not allowed", status=405)    
