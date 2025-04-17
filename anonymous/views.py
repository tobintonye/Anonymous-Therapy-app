from django.shortcuts import render, redirect
from .forms import AnonymousUserForm, LoginForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator # token generator 
from django.urls import reverse
from django.conf import settings

User = get_user_model()

def send_verification_email(user, request):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    verification_link = request.build_absolute_uri(
        reverse("anonymous:verifyemail", kwargs={"uidb64":uid, "token":token})
    )

    if user.role == User.UserRole.ANONYMOUS_USER:
        subject = "Verify Your Account"
        message = f"Hello {user.username},\n\nPlease verify your anonymous account by clicking the link below:\n\n{verification_link}"
    else:
        subject = "Verify Your Account"
        message = f"Hello {user.username},\n\nPlease verify your account by clicking the link below:\n\n{verification_link}"

    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

def verify_email(request, uidb64, token):
    """
    Verifies the user's email by checking the token.
    """
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        # Set the user's email as verified
        user.is_active = True
        user.save()
        # Log the user in after verification
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)
        messages.success(request, "Your email has been verified successfully.")
        return redirect('easetalk:home')
    else:
        return render(request, 'anonymous/verification_failed.html')

def resend_verification_link(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            if user.is_active:
                messages.info(request, 'Your email is already verified.')
                return redirect('anonymous:anonymoususer_login')
            # Generate new token and send verification email
            send_verification_email(user, request)
            messages.success(request, 'A new verification email has been sent. Please check your inbox.')
            return redirect('anonymous:verification_pending')
        except User.DoesNotExist:
            messages.error(request, 'No account with that email address exists.')
            return redirect('anonymous:anonymoususer_signup')
        
    return render(request, 'anonymous/resend_verification.html')

def verification_pending(request):
    return render(request, 'anonymous/verification_pending.html')

def register_anonymoususer(request):
    if request.method == "POST":
        form = AnonymousUserForm(request.POST)
        if form.is_valid():
            # Create user but set as inactive until email verification
            user = form.save(commit=False)
            user.is_active = False  # Set as inactive until verified
            user.set_password(form.cleaned_data["password1"])
            user.save()
            # Send email verification
            send_verification_email(user, request)
            # Redirect to verification pending page (create this template)
            messages.success(request, f'Account created successfully! Please check your email to verify your account.')
            return render(request, 'anonymous/verification_pending.html', {'email': user.email})
        else:
            messages.error(request, "Username or email already exists")
            return redirect('anonymous:anonymoususer_login')
    else:
        form = AnonymousUserForm()
        # ✅ Store signup path for social auth
    request.session["signup_path"] = "/anonymous/signup/" # not active for now
    return render(request, 'anonymous/SignUp.html', {"form":form})

def login_anonymoususer(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            user = authenticate(username=email, password=password)
            if user is not None:
                login(request, user)
                if not user.is_active:
                    messages.error(request, "Please verify your email before logging in.")
                    return redirect("therapy:verification_pending")  # Or show a message page
                if user.role != User.UserRole.ANONYMOUS_USER:
                    messages.error(request, "This email is already registered as an therapist.")
                    logout(request)
                    return redirect("therapy:login")
                # Handle "Remember Me" properly
                remember_me = form.cleaned_data.get("remember_me")
                if not remember_me:
                    request.session.set_expiry(0)  # Expires when browser closes
                else:
                    request.session.set_expiry(60 * 60 * 24 * 30)  # 30 days session
                messages.success(request, f"welcome back {request.user.username}")
                return redirect("easetalk:home")
            else:
                messages.error(request, "incorrect email address or password")
        else:
                messages.error(request, "Please enter a valid email and password.")
    else:
        form = LoginForm()
    return render(request, "anonymous/login.html", {"form": form})


# logout users
def logoutUser(request):
    username = request.user.username  # Get the username before logging out
    logout(request)
    messages.success(request, f'{username} logged out')
    return redirect("easetalk:index")