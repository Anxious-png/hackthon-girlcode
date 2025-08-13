from django.db import models
from django.contrib.auth.models import AbstractUser, User
from django.core.validators import MinLengthValidator, RegexValidator
from django.conf import settings
from django.db import models


# Create your models here.
class UserProfile(AbstractUser):

    user_type = models.CharField(max_length=30, choices=[
        ('agent', 'Mobile Money Agent'),
        ('student', 'Student'),
        ('vendor', 'Vendor'),
        ('other', 'Other'),
    ])
    phonenumber = models.CharField(max_length=15, blank=True, validators=[RegexValidator(regex=r'^07\d{8}$', message='Enter a valid Ugandan phone number')])
    email = models.EmailField(max_length=254, blank=True, 
   
    )
    location = models.CharField(max_length=100, blank=True)
    def __str__(self):
        return self.username

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
    event_type = models.CharField(max_length=50)  # e.g., 'failed_pin', 'login_attempt'
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
    related_number = models.CharField(max_length=20, blank=True)
    def __str__(self):
        return f"Message by {self.user} - {'Scam' if self.is_scam else 'Safe'}"