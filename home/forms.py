from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from .models import UserProfile
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import SavingGoal

from .models import InvestmentOption


class UserSignupForm(UserCreationForm):
    password = forms.CharField(widget=forms.PasswordInput)
    
    class Meta:
        model = UserProfile
        fields = ['username', 'email', 'password', 'phonenumber', 'user_type', 'account_number']

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'autofocus': True}))
    password = forms.CharField(widget=forms.PasswordInput)
    account_number = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Account Number '}))
    class Meta:
        model = UserProfile
        fields = ['username', 'password', 'account_number']

class SavingGoalForm(forms.ModelForm):
    class Meta:
        model = SavingGoal
        fields = ['goal_name', 'goal_amount', 'current_savings', 'duration']
        widgets = {
            'goal_name': forms.TextInput(attrs={'placeholder': 'e.g. Buy a car'}),
            'goal_amount': forms.NumberInput(attrs={'placeholder': 'Enter your goal amount'}),
            'current_savings': forms.NumberInput(attrs={'placeholder': 'How much have you saved so far?'}),
            'duration': forms.Select(choices=[('Monthly', 'Monthly'), ('Yearly', 'Yearly')]),
        }
from django import forms

class DepositForm(forms.Form):
    amount = forms.DecimalField(max_digits=12, decimal_places=2, min_value=1000, label="Deposit Amount (UGX)")

class AddSavingForm(forms.Form):
    amount = forms.DecimalField(max_digits=12, decimal_places=2, min_value=1000, label="Amount to Save (UGX)")

class WithdrawForm(forms.Form):
    amount = forms.DecimalField(max_digits=12, decimal_places=2, min_value=1000, label="Amount to Withdraw (UGX)")


class InvestmentForm(forms.ModelForm):
    class Meta:
        model = InvestmentOption
        fields = [
            'name', 
            'category', 
            'description', 
            'min_amount', 
    
        ]

    def _init_(self, *args, **kwargs):
        super()._init_(*args, **kwargs)
        # Customize field attributes
        self.fields['name'].widget.attrs.update({'placeholder': 'Enter investment name'})
        self.fields['category'].widget.attrs.update({'class': 'form-select'})
        self.fields['description'].widget.attrs.update({'placeholder': 'Brief description', 'rows': 3})
      