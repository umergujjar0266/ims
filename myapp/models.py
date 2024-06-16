from django.contrib.auth.models import AbstractUser
from django.db import models, transaction
import uuid
from django.core.exceptions import ValidationError

class CustomUser(AbstractUser):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    PLAN_CHOICES = [
        (10, '$10'),
        (100, '$100'),
        (200, '$200'),
        (500, '$500'),
        (800, '$800'),
        (1000, '$1000'),
    ]
    plan = models.IntegerField(choices=PLAN_CHOICES, null=True, blank=True)
    joined_referral_id = models.CharField(max_length=8, null=True, blank=True)
    user_referral_id = models.CharField(max_length=8, unique=True, null=True, blank=True)
    wallet_id = models.PositiveIntegerField(unique=True, null=True, blank=True)
    wallet_balance = models.PositiveIntegerField(default=0)
    phone_number = models.CharField(max_length=20, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.pk:  # if the instance is being created
            # Generate user_referral_id and wallet_id only if they are not provided
            if not self.user_referral_id:
                self.user_referral_id = str(uuid.uuid4())[:8]  # Generate a unique ID of length 8
            if not self.wallet_id:
                self.wallet_id = int(str(uuid.uuid4().int)[:8])  # Generate a unique ID of length 8

        super().save(*args, **kwargs)
        
        # Create or update the Referral model
        Referral.objects.update_or_create(
            user=self,
            defaults={
                'user_referral_id': self.user_referral_id,
                'joined_referral_id': self.joined_referral_id
            }
        )

    def __str__(self):
        return self.username

class OverallAlert(models.Model):  # Adjust model name to follow Python naming conventions
    message = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.message  # Define a meaningful string representation for admin interface

class Alert(models.Model):
    message = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    recipient = models.CharField(max_length=100 ,null=True)  # New field to store the recipient username

    def __str__(self):
        return self.message

class ContactMessage(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField()
    response = models.CharField(max_length=255 ,blank=True, default="not respond yet")
    date_sent = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message recieved  by {self.sender}"

class Referral(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    user_referral_id = models.CharField(max_length=8)
    joined_referral_id = models.CharField(max_length=8, null=True, blank=True)

    @property
    def joins(self):
        return self.count_joins()

    def count_joins(self):
        return Referral.objects.filter(joined_referral_id=self.user_referral_id).count()

    def __str__(self):
        return f"Referral for {self.user.username}"
from django.db import models

class Wallet(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.user.wallet_balance = self.balance
        self.user.save()
        super().save(*args, **kwargs)

    @property
    def balance(self):
        return self.user.wallet_balance

    @balance.setter
    def balance(self, value):
        self.user.wallet_balance = value
        self.user.save()

    @property
    def w_id(self):
        return self.user.wallet_id

    @w_id.setter
    def w_id(self, value):
        self.user.wallet_id = value
        self.user.save()

    def __str__(self):
        return f"{self.user.username}'s Wallet"


class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('deposit', 'Deposit'),
        ('withdraw', 'Withdraw'),
    )
    
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type.capitalize()} of {self.amount} to {self.wallet.user.username}'s Wallet"

    def save(self, *args, **kwargs):
        if self.transaction_type == 'withdraw' and self.amount > self.wallet.balance:
            raise ValidationError("Insufficient balance for withdrawal.")
        
        with transaction.atomic():
            if self.transaction_type == 'withdraw':
                self.wallet.balance -= self.amount
            elif self.transaction_type == 'deposit':
                self.wallet.balance += self.amount
            self.wallet.save()
            super().save(*args, **kwargs)
