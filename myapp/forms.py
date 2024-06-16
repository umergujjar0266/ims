
from django import forms
from django.contrib.auth.forms import UserCreationForm,UserChangeForm
from .models import CustomUser,Wallet,Alert,ContactMessage
from django.contrib.auth import get_user_model

class AdminTransactionForm(forms.Form):
    TRANSACTION_CHOICES = [
        ('deposit', 'Deposit'),
        ('withdraw', 'Withdraw'),
    ]
    user = forms.ModelChoiceField(queryset=Wallet.objects.all(), label="Select User Wallet")
    transaction_type = forms.ChoiceField(choices=TRANSACTION_CHOICES)
    amount = forms.DecimalField(max_digits=10, decimal_places=2)



class UserRegistrationForm(UserCreationForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['first_name','last_name','username', 'email','plan','joined_referral_id','phone_number'] 

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'username','email','phone_number','joined_referral_id')
class PasswordChangeForm(forms.Form):
    old_password = forms.CharField(label='Old Password', widget=forms.PasswordInput)
    new_password1 = forms.CharField(label='New Password', widget=forms.PasswordInput)
    new_password2 = forms.CharField(label='Confirm New Password', widget=forms.PasswordInput)

class AlertForm(forms.ModelForm):
    class Meta:
        model = Alert
        fields = ['message', 'recipient']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['recipient'].widget = forms.Select(choices=self.get_recipient_choices())

    def get_recipient_choices(self):
        User = get_user_model()
        choices = [(user.username, user.username) for user in User.objects.all()]
        return choices

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['message']