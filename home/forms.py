from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import UserProfile, SavingGoal, InvestmentOption


# ─────────────────────────────────────────────────────────────────────────────
# AUTH FORMS
# ─────────────────────────────────────────────────────────────────────────────

class UserSignupForm(UserCreationForm):
    """
    Signup form. Account number is auto-generated — not shown here.
    User sets their transaction PIN during signup.
    """
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'your@email.com'}))
    phonenumber = forms.CharField(
        max_length=15, required=True,
        widget=forms.TextInput(attrs={'placeholder': '07XXXXXXXX'}),
        help_text="Ugandan number starting with 07"
    )
    user_type = forms.ChoiceField(choices=UserProfile.USER_TYPE_CHOICES)
    location = forms.CharField(
        max_length=100, required=False,
        widget=forms.TextInput(attrs={'placeholder': 'e.g. Kampala, Uganda'})
    )
    transaction_pin = forms.CharField(
        min_length=4, max_length=4,
        widget=forms.PasswordInput(attrs={'placeholder': '4-digit PIN', 'maxlength': '4'}),
        help_text="Set a 4-digit PIN for authorising transactions",
        label="Transaction PIN"
    )
    confirm_transaction_pin = forms.CharField(
        min_length=4, max_length=4,
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm PIN', 'maxlength': '4'}),
        label="Confirm Transaction PIN"
    )

    class Meta:
        model = UserProfile
        fields = ['username', 'email', 'phonenumber', 'user_type', 'location',
                  'password1', 'password2', 'transaction_pin', 'confirm_transaction_pin']

    def clean(self):
        cleaned = super().clean()
        pin = cleaned.get('transaction_pin', '')
        confirm = cleaned.get('confirm_transaction_pin', '')
        if pin and not pin.isdigit():
            self.add_error('transaction_pin', 'PIN must contain digits only.')
        if pin and confirm and pin != confirm:
            self.add_error('confirm_transaction_pin', 'PINs do not match.')
        return cleaned


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'autofocus': True, 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))


# ─────────────────────────────────────────────────────────────────────────────
# TRANSACTION PIN FORMS
# ─────────────────────────────────────────────────────────────────────────────

class SetPinForm(forms.Form):
    """Used when a user wants to change/set their transaction PIN."""
    new_pin = forms.CharField(
        min_length=4, max_length=4,
        widget=forms.PasswordInput(attrs={'placeholder': '4-digit PIN', 'maxlength': '4'}),
        label="New Transaction PIN"
    )
    confirm_pin = forms.CharField(
        min_length=4, max_length=4,
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm PIN', 'maxlength': '4'}),
        label="Confirm PIN"
    )

    def clean(self):
        cleaned = super().clean()
        pin = cleaned.get('new_pin', '')
        confirm = cleaned.get('confirm_pin', '')
        if pin and not pin.isdigit():
            self.add_error('new_pin', 'PIN must be digits only.')
        if pin and confirm and pin != confirm:
            self.add_error('confirm_pin', 'PINs do not match.')
        return cleaned


class PinVerifyForm(forms.Form):
    """Inline PIN entry used on confirmation screens."""
    pin = forms.CharField(
        min_length=4, max_length=4,
        widget=forms.PasswordInput(attrs={
            'placeholder': '● ● ● ●',
            'maxlength': '4',
            'class': 'pin-input',
            'autocomplete': 'off',
            'inputmode': 'numeric',
        }),
        label="Enter your 4-digit Transaction PIN"
    )

    def clean_pin(self):
        pin = self.cleaned_data.get('pin', '')
        if not pin.isdigit():
            raise forms.ValidationError("PIN must be digits only.")
        return pin


# ─────────────────────────────────────────────────────────────────────────────
# FINANCIAL FORMS
# ─────────────────────────────────────────────────────────────────────────────

class DepositForm(forms.Form):
    amount = forms.DecimalField(
        max_digits=12, decimal_places=2, min_value=1000,
        label="Amount to Deposit (UGX)",
        widget=forms.NumberInput(attrs={'placeholder': 'Minimum UGX 1,000'})
    )
    description = forms.CharField(
        max_length=200, required=False,
        widget=forms.TextInput(attrs={'placeholder': 'e.g. Salary, Business income (optional)'}),
        label="Description (optional)"
    )


class WithdrawForm(forms.Form):
    amount = forms.DecimalField(
        max_digits=12, decimal_places=2, min_value=1000,
        label="Amount to Withdraw (UGX)",
        widget=forms.NumberInput(attrs={'placeholder': 'Minimum UGX 1,000'})
    )
    reason = forms.CharField(
        max_length=200, required=False,
        widget=forms.TextInput(attrs={'placeholder': 'e.g. Rent, School fees (optional)'}),
        label="Reason (optional)"
    )


class AddSavingForm(forms.Form):
    amount = forms.DecimalField(
        max_digits=12, decimal_places=2, min_value=1000,
        label="Amount to Save (UGX)",
        widget=forms.NumberInput(attrs={'placeholder': 'Minimum UGX 1,000'})
    )


class SavingGoalForm(forms.ModelForm):
    class Meta:
        model = SavingGoal
        fields = ['goal_name', 'goal_amount', 'duration']
        widgets = {
            'goal_name': forms.TextInput(attrs={'placeholder': 'e.g. Buy a car, School fees'}),
            'goal_amount': forms.NumberInput(attrs={'placeholder': 'Target amount in UGX'}),
            'duration': forms.Select(),
        }


class InvestmentForm(forms.ModelForm):
    class Meta:
        model = InvestmentOption
        fields = ['name', 'category', 'description', 'min_amount']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Investment name'}),
            'description': forms.Textarea(attrs={'placeholder': 'Brief description', 'rows': 3}),
        }
