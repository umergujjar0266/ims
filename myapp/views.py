from django.core.exceptions import ValidationError
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Alert, CustomUser, ContactMessage, OverallAlert, Wallet, Transaction
from .forms import UserRegistrationForm, CustomUserChangeForm, ContactForm, AdminTransactionForm
from django.db.models import Sum

@login_required
def index(request):
    if request.user.is_authenticated:
        user_status = request.user.status  # Get the status of the logged-in user
        if user_status == 'pending':
            return render(request, 'myapp/pending_page.html')  # Display a page indicating pending status
        elif user_status == 'approved':
            username = request.user.username
            try:
                custom_user = CustomUser.objects.get(username=username)
                wallet_balance = custom_user.wallet_balance
                if wallet_balance is None or wallet_balance == 0:
                    error_message = "Contact the admin if you are receiving this error message."
                    return render(request, 'myapp/index.html', {'error_message': error_message})
                else:
                    wallet = get_object_or_404(Wallet, user=request.user)
                    transactions = Transaction.objects.filter(wallet=wallet).order_by('-timestamp')
                    return render(request, 'myapp/index.html', {
                        'wallet': wallet,
                        'transactions': transactions,
                    })
            except CustomUser.DoesNotExist:
                error_message = "User does not have a corresponding CustomUser object."
                return render(request, 'myapp/index.html', {'error_message': error_message})
        else:
            return render(request, 'myapp/declined_page.html')  # Display a page indicating declined status
    else:
        return redirect('login')  # Redirect unauthenticated users to the login page


@login_required
def user_dashboard(request):
    wallet = get_object_or_404(Wallet, user=request.user)
    transactions = Transaction.objects.filter(wallet=wallet).order_by('-timestamp')
    return render(request, 'myapp/user_dashboard.html', {
        'wallet': wallet,
        'transactions': transactions,
    })


@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect('user_dashboard')
    
    wallets = Wallet.objects.all()
    transactions = Transaction.objects.all().order_by('-timestamp')
    total_deposited = Transaction.objects.filter(transaction_type='deposit').aggregate(Sum('amount'))['amount__sum'] or 0.00
    total_withdrawn = Transaction.objects.filter(transaction_type='withdraw').aggregate(Sum('amount'))['amount__sum'] or 0.00

    if request.method == 'POST':
        form = AdminTransactionForm(request.POST)
        if form.is_valid():
            wallet = form.cleaned_data['user']
            transaction_type = form.cleaned_data['transaction_type']
            amount = form.cleaned_data['amount']

            try:
                transaction = Transaction(wallet=wallet, transaction_type=transaction_type, amount=amount)
                transaction.save()
                messages.success(request, f"{transaction_type.capitalize()} of {amount} was successful.")
            except ValidationError as e:
                messages.error(request, e.message)
        else:
            messages.error(request, "Invalid form submission.")
    else:
        form = AdminTransactionForm()

    return render(request, 'myapp/admin_dashboard.html', {
        'wallets': wallets,
        'transactions': transactions,
        'total_deposited': total_deposited,
        'total_withdrawn': total_withdrawn,
        'form': form,
    })



def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')  
            else:
                messages.error(request, 'Invalid username or password. Please try again.')
    else:
        form = AuthenticationForm()
    return render(request, 'myapp/login.html', {'form': form})
def user_logout(request):
    logout(request)
    return redirect('user_login')
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.status = 'pending'
            user.save()
            messages.success(request, 'Your account has been registered successfully!')
            return redirect('user_login')
    else:
        form = UserRegistrationForm()
    return render(request, 'myapp/register.html', {'form': form})

@login_required
def plan(request):
    return render(request, 'myapp/plan.html')

@login_required
def alert_list(request):
    user = request.user  # Get the current user
    alerts = Alert.objects.filter(recipient=user)  # Filter alerts based on the recipient
    overall_alerts = OverallAlert.objects.all()
    return render(request, 'myapp/alert_list.html', {'alerts': alerts, 'overall_alerts': overall_alerts})

@login_required
def profile(request):
    return render(request, 'myapp/profile.html')

@login_required
def profile_edit(request):
    user_form = CustomUserChangeForm(instance=request.user)
    password_form = PasswordChangeForm(request.user)

    if request.method == 'POST':
        if 'change_personal_info' in request.POST:  # If user wants to change personal info
            user_form = CustomUserChangeForm(request.POST, instance=request.user)
            if user_form.is_valid():
                user_form.save()
                return redirect('profile')  # Redirect to profile page
        elif 'change_password' in request.POST:  # If user wants to change password
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, request.user)  # Update session to prevent log out
                return redirect('profile')  # Redirect to profile page

    return render(request, 'myapp/profile_edit.html', {'user_form': user_form, 'password_form': password_form})


@login_required
def user_contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user  # Assuming you have user authentication
            message.save()
            return redirect('contact_success')  # Redirect to a success page after submission
    else:
        form = ContactForm()
    
    # Fetch messages sent by the current user
    messages = ContactMessage.objects.filter(sender=request.user)
    return render(request, 'myapp/contact.html', {'form': form, 'messages': messages})


@login_required
def contact_success(request):
    return render(request, 'myapp/contact_success.html')
