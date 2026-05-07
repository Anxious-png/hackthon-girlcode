from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, MinLengthValidator
from django.conf import settings
from django.utils import timezone
import uuid
import hashlib
import random


def generate_account_number():
    """Generate a fixed, structured account number: SG-YYYY-XXXXXXXX"""
    year = timezone.now().year
    unique = str(random.randint(10000000, 99999999))
    return f"SG{year}{unique}"


class UserProfile(AbstractUser):
    USER_TYPE_CHOICES = [
        ('agent', 'Mobile Money Agent'),
        ('student', 'Student'),
        ('vendor', 'Vendor'),
        ('other', 'Other'),
    ]

    user_type = models.CharField(max_length=30, choices=USER_TYPE_CHOICES, default='other')
    phonenumber = models.CharField(
        max_length=15, blank=True,
        validators=[RegexValidator(regex=r'^07\d{8}$', message='Enter a valid Ugandan phone number (07XXXXXXXX)')]
    )
    email = models.EmailField(max_length=254, blank=True)
    location = models.CharField(max_length=100, blank=True)

    # Fixed account number — assigned once at signup, never changes
    account_number = models.CharField(max_length=20, unique=True, null=True, blank=True)

    # Transaction PIN — stored as SHA-256 hash, separate from login password
    transaction_pin_hash = models.CharField(max_length=64, blank=True, null=True)

    # PIN security: lock after 3 failed attempts
    pin_attempts = models.PositiveSmallIntegerField(default=0)
    pin_locked = models.BooleanField(default=False)

    # Whether user has set up their PIN
    pin_set = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.account_number:
            # Keep generating until unique
            acc = generate_account_number()
            while UserProfile.objects.filter(account_number=acc).exists():
                acc = generate_account_number()
            self.account_number = acc
        super().save(*args, **kwargs)

    def set_transaction_pin(self, raw_pin):
        """Hash and store the 4-digit transaction PIN."""
        self.transaction_pin_hash = hashlib.sha256(raw_pin.encode()).hexdigest()
        self.pin_set = True
        self.pin_attempts = 0
        self.pin_locked = False
        self.save()

    def verify_transaction_pin(self, raw_pin):
        """
        Verify PIN. Returns True/False.
        Locks account after 3 consecutive failures.
        """
        if self.pin_locked:
            return False
        hashed = hashlib.sha256(raw_pin.encode()).hexdigest()
        if self.transaction_pin_hash == hashed:
            self.pin_attempts = 0
            self.save(update_fields=['pin_attempts'])
            return True
        else:
            self.pin_attempts += 1
            if self.pin_attempts >= 3:
                self.pin_locked = True
            self.save(update_fields=['pin_attempts', 'pin_locked'])
            return False

    def __str__(self):
        return f"{self.username} ({self.account_number})"


class BankAccount(models.Model):
    """
    Each user has exactly ONE bank account.
    The account number mirrors the user's account_number for consistency.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bank_account'
    )
    bank_name = models.CharField(max_length=100, default="SilentGuard Bank")
    balance = models.DecimalField(max_digits=14, decimal_places=2, default=0.00)
    is_frozen = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    @property
    def account_number(self):
        """Account number is always the user's fixed account number."""
        return self.user.account_number

    def deposit(self, amount):
        if self.is_frozen:
            raise ValueError("Account is frozen. Contact support.")
        from decimal import Decimal
        self.balance += Decimal(str(amount))
        self.save(update_fields=['balance'])

    def withdraw(self, amount):
        if self.is_frozen:
            raise ValueError("Account is frozen. Contact support.")
        from decimal import Decimal
        amount = Decimal(str(amount))
        if amount > self.balance:
            raise ValueError("Insufficient funds.")
        self.balance -= amount
        self.save(update_fields=['balance'])
        return True

    def __str__(self):
        return f"{self.user.username} — {self.account_number} — UGX {self.balance:,.0f}"


class SavingGoal(models.Model):
    DURATION_CHOICES = [
        ('Monthly', 'Monthly'),
        ('Quarterly', 'Quarterly'),
        ('Yearly', 'Yearly'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    goal_name = models.CharField(max_length=100, default="Annual Savings Goal")
    goal_amount = models.DecimalField(max_digits=12, decimal_places=2)
    current_savings = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    duration = models.CharField(max_length=20, choices=DURATION_CHOICES, default="Yearly")
    created_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)

    @property
    def progress_percent(self):
        if self.goal_amount > 0:
            pct = (self.current_savings / self.goal_amount) * 100
            return min(round(float(pct), 2), 100.0)
        return 0.0

    @property
    def remaining(self):
        from decimal import Decimal
        r = self.goal_amount - self.current_savings
        return max(r, Decimal('0'))

    def __str__(self):
        return f"{self.goal_name} — {self.progress_percent}%"


class Transaction(models.Model):
    CATEGORY_CHOICES = [
        ("Deposit", "Deposit"),
        ("Withdrawal", "Withdrawal"),
        ("Transfer", "Transfer to Savings"),
        ("Purchase", "Purchase"),
        ("Bill Payment", "Bill Payment"),
        ("Other", "Other"),
    ]

    STATUS_CHOICES = [
        ("completed", "Completed"),
        ("pending", "Pending"),
        ("failed", "Failed"),
        ("reversed", "Reversed"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reference = models.CharField(max_length=20, unique=True, blank=True, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default="Other")
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="completed")
    timestamp = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = f"TXN{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.reference} — {self.category} UGX {self.amount}"


class FraudReport(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    scammer_number = models.CharField(max_length=20)
    message = models.TextField()
    report_reason = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report by {self.user} — {self.scammer_number}"


class SuspiciousActivityLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=50)
    location = models.CharField(max_length=100, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.event_type} — {self.user} at {self.timestamp}"


class NumberBlacklist(models.Model):
    phone_number = models.CharField(max_length=20, unique=True)
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    report_count = models.PositiveIntegerField(default=1)
    first_reported = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Blacklisted: {self.phone_number} ({self.report_count} reports)"


class RiskyTransaction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    receiver_number = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    flagged = models.BooleanField(default=False)
    reason_flagged = models.TextField(blank=True)
    checked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.receiver_number} — {self.amount} by {self.user}"


class EducationalContent(models.Model):
    CATEGORY_CHOICES = [
        ('Savings', 'Savings'),
        ('Fraud Prevention', 'Fraud Prevention'),
        ('Financial Planning', 'Financial Planning'),
    ]
    ICON_CHOICES = [
        ('fa-piggy-bank', 'Piggy Bank'),
        ('fa-bullseye', 'Bullseye'),
        ('fa-chart-pie', 'Chart Pie'),
        ('fa-first-aid', 'First Aid'),
        ('fa-exclamation-triangle', 'Warning'),
        ('fa-shield-alt', 'Shield'),
        ('fa-shopping-cart', 'Shopping Cart'),
        ('fa-layer-group', 'Layers'),
        ('fa-user-slash', 'User Slash'),
        ('fa-mobile-alt', 'Mobile'),
        ('fa-lock', 'Lock'),
        ('fa-chart-line', 'Chart Line'),
    ]

    title = models.CharField(max_length=255)
    summary = models.TextField(default='', help_text="Short preview shown on the card (2-3 sentences)")
    content = models.TextField(help_text="Full article content shown when user clicks Learn More")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Savings')
    icon = models.CharField(max_length=50, choices=ICON_CHOICES, default='fa-piggy-bank')
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
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True
    )
    message_text = models.TextField()
    is_scam = models.BooleanField(default=False)
    detected_keywords = models.TextField(blank=True)
    scanned_at = models.DateTimeField(auto_now_add=True)
    related_number = models.CharField(max_length=20, null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    confidence_score = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{'SCAM' if self.is_scam else 'Safe'} — {self.user} — {self.scanned_at:%Y-%m-%d}"


class InvestmentOption(models.Model):
    CATEGORY_CHOICES = [
        ('Investment', 'Investment'),
        ('Insurance', 'Insurance'),
        ('Real Estate', 'Real Estate'),
        ('Vehicle Financing', 'Vehicle Financing'),
        ('Shares', 'Shares'),
    ]
    RISK_CHOICES = [
        ('Low', 'Low'),
        ('Moderate', 'Moderate'),
        ('High', 'High'),
    ]

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Investment')
    description = models.TextField()
    min_amount = models.DecimalField(max_digits=12, decimal_places=2)
    risk_level = models.CharField(max_length=20, choices=RISK_CHOICES)
    return_rate = models.DecimalField(max_digits=5, decimal_places=2, help_text="Expected return % per year")
    image_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.category})"
