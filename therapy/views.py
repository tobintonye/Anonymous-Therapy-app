from django.shortcuts import render, redirect, get_object_or_404
from .forms import SignUpform, LoginForm, UserProfileForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Specialization, TherapistProfile
from django.contrib.auth.decorators import login_required
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
        reverse("therapy:verifyemail", kwargs={"uidb64":uid, "token":token})
    )

    if user.role == User.UserRole.THERAPIST:
        subject = "Verify Your Therapist Account"
        message = f"Hello {user.username},\n\nPlease verify your therapist account by clicking the link below:\n\n{verification_link}"
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
        
        messages.success(request, "Your email has been verified successfully. You can now create your profile.")
        return redirect('therapy:createprofile')
    else:
        return render(request, 'therapy/verification_failed.html')

def resend_verification_link(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            if user.is_active:
                messages.info(request, 'Your email is already verified.')
                return redirect('therapy:login')
            # Generate new token and send verification email
            send_verification_email(user, request)
            
            messages.success(request, 'A new verification email has been sent. Please check your inbox.')
            return redirect('therapy:verification_pending')
            
        except User.DoesNotExist:
            messages.error(request, 'No account with that email address exists.')
            return redirect('therapy:register')
    
    return render(request, 'therapy/resend_verification.html')

def verification_pending(request):
    return render(request, 'therapy/verification_pending.html')

# Add a decorator to protect routes that require email verification
def email_verification_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_active:
            return view_func(request, *args, **kwargs)
        else:
            messages.warning(request, "Please verify your email before accessing this page.")
            return redirect('therapy:login')  # Or a custom page explaining verification
    return wrapper

''''

# regiterusers no validation yet just for development
def registerTherapist(request):
    if request.user.is_authenticated:
        messages.error(request,'logged you out')
        logout(request)
        return redirect('therapy:register')
    
    if request.user.is_authenticated and hasattr(request.user, "role"):
         if request.user.role != User.UserRole.THERAPIST:
             messages.error(request, "You are not authorized")
             logout(request)
             return redirect('easetalk:index')
         
    if request.method == "POST":
        form = SignUpform(request.POST)
        if form.is_valid():
            user = form.save(commit=False) # don't authenticate the user yet
            user.set_password(form.cleaned_data["password1"])
            user.save()

             # Specify the backend explicitly
            user.backend = 'django.contrib.auth.backends.ModelBackend' 

            login(request, user)
            # Send email verification
            send_verification_email(user, request)
           
            messages.success(request, f'Account {request.user.username} created successfully! Create a profile')
            return redirect('therapy:createprofile')
        else:
             messages.warning(request, f"username or email already exists")
             return redirect('therapy:register')
    else:
        form = SignUpform()
    # ✅ Store signup path for social auth
    request.session["si6gnup_path"] = "/therapy/register/"
    return render(request, 'therapy/signup.html', {'form':form})
'''

def registerTherapist(request):
    if request.user.is_authenticated:
        messages.error(request, 'Logged you out')
        logout(request)
        return redirect('therapy:register')
    
    if request.user.is_authenticated and hasattr(request.user, "role"):
         if request.user.role != User.UserRole.THERAPIST:
             messages.error(request, "You are not authorized")
             logout(request)
             return redirect('easetalk:index')
    
    if request.method == "POST":
        form = SignUpform(request.POST)
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
            return render(request, 'therapy/verification_pending.html', {'email': user.email})
        else:
            messages.warning(request, "Username or email already exists")
            return redirect('therapy:login')
    else:
        form = SignUpform()
    request.session["signup_path"] = "/therapy/register/" # not active yet
    return render(request, 'therapy/signup.html', {'form':form})

# login a therapist 
from django.contrib.auth import get_user_model

User = get_user_model()

def LoginUser(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")

            try:
                user = User.objects.get(email=email)
                if not user.check_password(password):
                    raise User.DoesNotExist  # Pretend not found if password wrong
            except User.DoesNotExist:
                messages.error(request, "Incorrect username or password")
                return render(request, "therapy/login.html", {"form": form})

            if not user.is_active:
                messages.error(request, "Please verify your email before logging in.")
                return redirect("therapy:verification_pending")

            if user.role == User.UserRole.ANONYMOUS_USER:
                messages.error(request, "This email is already registered as an anonymous user.")
                logout(request)
                return redirect("therapy:login")

            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)

            # Handle "Remember Me"
            remember_me = form.cleaned_data.get("remember_me")
            if not remember_me:
                request.session.set_expiry(0)
            else:
                request.session.set_expiry(60 * 60 * 24 * 30)

            # Therapist must have profile
            if user.role == User.UserRole.THERAPIST and not TherapistProfile.objects.filter(user=user).exists():
                messages.warning(request, "You must create a profile before continuing.")
                return redirect("therapy:createprofile")

            messages.success(request, f"Welcome back, {request.user.username}")
            return redirect("easetalk:home")
        else:
            messages.error(request, "Please enter a valid email and password.")
        return render(request, "therapy/login.html", {"form": form})
    else:
        form = LoginForm()
    return render(request, "therapy/login.html", {"form": form})



# logout users
def logoutUser(request):
    username = request.user.username  # Get the username before logging out
    logout(request)
    messages.success(request, f'{username} logged out')
    return redirect("easetalk:index")


# a view to allow therapist create profiles
def createprofile(request):
    if not request.user.is_authenticated:
        messages.error(request, 'You do not have access to this page')
        return redirect('therapy:login')
    
    if request.user.role != User.UserRole.THERAPIST:
        messages.error(request, "You are not authorized")
        return redirect("easetalk:home")
    
    # check if the user already has a profile
    if TherapistProfile.objects.filter(user=request.user).exists():
        messages.error(request, "You already have a profile and cannot create another one")
        therapist_profile = TherapistProfile.objects.get(user=request.user)  # Fetch the therapist profile
        return redirect('therapy:therapistprofile', therapist_id=therapist_profile.id)  # Use ID instead of username
    
    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES) # Bound form with an image field, data from the request
        if form.is_valid():
            try:
                # save the new profile and associate it with the current user
                therapist_profile = form.save(commit=False) 
                therapist_profile.user = request.user # associating the profile with the current logged-in user
                therapist_profile.save()
                # Handle ManyToManyField for specializations
                selected_specializations = request.POST.getlist('specializations', [])
                specializations_objects = Specialization.objects.filter(id__in=selected_specializations)
                therapist_profile.specializations.set(specializations_objects) # Set the specialization relationships  
                messages.success(request, f"Profile created {request.user.username}")
                return redirect('therapy:therapistprofile', therapist_id=therapist_profile.id)
            except Exception as e:
                messages.error(request, f'An error occured: {e}')
                return redirect('therapy:createprofile')
        else:
            messages.error(request, "There was an error with your submission.")
    else:
        form = UserProfileForm()
    return render(request, 'therapy/createprofile.html', {"form": form})


# therapist to view their profile 
def therapistprofile_view(request, therapist_id):
    if not request.user.is_authenticated:
        messages.error(request, 'You do not have access to this page')
        return redirect('therapy:login')
    
    if request.user.role != User.UserRole.THERAPIST:
        messages.error(request, "You are not authorized")
        return redirect("easetalk:home")
    try:
        therapistprofile = TherapistProfile.objects.get(id=therapist_id)
    except TherapistProfile.DoesNotExist:
        therapistprofile = None
    return render(request, 'therapy/therapistprofile.html', {'therapist': therapistprofile})


# edit profile
@login_required
def edit_therapist_profile(request):
    if request.user.role != User.UserRole.THERAPIST:
        messages.error(request, "You are not authorized")
        return redirect("easetalk:home")
    therapist_profile = get_object_or_404(TherapistProfile, user=request.user) # get therapist profile or return a 404 status code
    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=therapist_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated')
            return redirect('therapy:therapistprofile', therapist_id=therapist_profile.id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserProfileForm(instance=therapist_profile)
    return render(request, 'therapy/editprofile.html', {'form':form})


# allow all users view therapist profile 
def profiledetail_view(request, therapist_id):
    profile = get_object_or_404(TherapistProfile, id=therapist_id)
    therapists = profile.user
    return render(request, 'therapy/profiledetail.html', {'profile':profile, 'therapist': profile,  })