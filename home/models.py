from django.db import models
from django.contrib.auth.models import AbstractUser, User
from django.core.validators import MinLengthValidator, RegexValidator
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import *
import uuid


# Create your models here.
class UserProfile(AbstractUser):

    user_type = models.CharField(max_length=30, choices=[
        ('agent', 'Mobile Money Agent'),
        ('student', 'Student'),
        ('vendor', 'Vendor'),
        ('other', 'Other'),
    ])
    phonenumber = models.CharField(max_length=15, blank=True, validators=[RegexValidator(regex=r'^07\d{8}$', message='Enter a valid Ugandan phone number')])
    email = models.EmailField(max_length=254, blank=True, )
    location = models.CharField(max_length=100, blank=True)
    account_number = models.CharField(max_length=20, unique=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Automatically assign an account number if missing
        if not self.account_number:
            import random
            self.account_number = f"UG{random.randint(10000000,99999999)}"
        super().save(*args, **kwargs)
    
    
    def __str__(self):
        return f"{self.username} ({self.account_number})"

class Transaction(models.Model):
    CATEGORY_CHOICES = [
        ("Deposit", "Deposit"),
        ("Withdrawal", "Withdrawal"),
        ("Transfer", "Transfer"),
        ("Purchase", "Purchase"),
        ("Bill Payment", "Bill Payment"),
        ("Other", "Other"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, null=False, default="Other")
    description = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return f"{self.category} - UGX {self.amount}"

class BankAccount(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bank_name = models.CharField(max_length=100, default="ABSA Bank")
    account_number = models.CharField(max_length=20, unique=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    def deposit(self, amount):
        self.balance += amount
        self.save()
    def save(self, *args, **kwargs):
        if not self.account_number:
            self.account_number = str(uuid.uuid4().int)[:10]  
        super().save(*args, **kwargs)

    def withdraw(self, amount):
        if amount <= self.balance:
            self.balance -= amount
            self.save()
            return True
        return False

    def __str__(self):
        return f"{self.user}'s Account - UGX {self.balance}"






class SavingGoal(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    goal_name = models.CharField(max_length=100, default="Annual Savings Goal")
    goal_amount = models.DecimalField(max_digits=10, decimal_places=2)
    current_savings = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    duration = models.CharField(max_length=20, default="Yearly")
    created_at = models.DateTimeField(auto_now_add=True)
    @property
    def progress_percent(self):
        if self.goal_amount > 0:
            return round((self.current_savings / self.goal_amount) * 100, 2)
        return 0

    def __str__(self):
        return f"{self.goal_name} ({self.progress_percent}%)"
    


class FraudReport(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    scammer_number = models.CharField(max_length=20)
    message = models.TextField()
    report_reason = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Report by {self.user} - {self.scammer_number}"

class SuspiciousActivityLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=50) 
    location = models.CharField(max_length=100, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    def __str__(self):
        return f"{self.event_type} for {self.user} at {self.timestamp}"

class NumberBlacklist(models.Model):
    phone_number = models.CharField(max_length=20, unique=True)
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    report_count = models.PositiveIntegerField(default=1)
    first_reported = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Blacklisted Number: {self.phone_number} (Reported {self.report_count} times)"

class RiskyTransaction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    receiver_number = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    flagged = models.BooleanField(default=False)
    reason_flagged = models.TextField(blank=True)
    checked_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.receiver_number} - {self.amount} by {self.user}"

class EducationalContent(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    language = models.CharField(max_length=30, default='English')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Feedback(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.user} at {self.submitted_at}"


class ScannedMessage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message_text = models.TextField()
    is_scam = models.BooleanField(default=False)
    detected_keywords = models.TextField(blank=True)
    scanned_at = models.DateTimeField(auto_now_add=True)
    related_number = models.CharField(max_length=20, null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    confidence_score = models.FloatField(null=True, blank=True) 
    def __str__(self):
        return f"Message by {self.user} - {'Scam' if self.is_scam else 'Safe'}"
    
class InvestmentOption(models.Model):
    CATEGORY_CHOICES = [
        ('Investment', 'Investment'),
        ('Insurance', 'Insurance'),
        ('Real Estate', 'Real Estate'),
        ('Vehicle Financing', 'Vehicle Financing'),
        ('Shares', 'Shares'),
    ]
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Investment',null=True, blank=True)
    description = models.TextField()
    min_amount = models.DecimalField(max_digits=12, decimal_places=2)
    risk_level = models.CharField(max_length=20, choices=[
        ('Low', 'Low'),
        ('Moderate', 'Moderate'),
        ('High', 'High'),
    ])
    return_rate = models.DecimalField(max_digits=5, decimal_places=2, help_text="Expected return in % per year")
    image_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.category})"



