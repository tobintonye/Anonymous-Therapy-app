from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import TherapistProfile, Specialization
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox  
User = get_user_model() # return current active users 

class SignUpform(UserCreationForm): 
    username = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'username'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email'}))
    password1 = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    password2 = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'confirm password'}))
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    # check to see if the email already email
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

# check if a username already exists
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists")
        return username
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.UserRole.THERAPIST # Assign therapist role
        if commit:
            user.save()
        return user
    
class LoginForm(forms.Form): 
    email = forms.EmailField(max_length=255, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'email'}))
    password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    remember_me = forms.BooleanField(required=False, initial=False, widget=forms.CheckboxInput())

    # check if username exist -> but using email for authentication
    def clean_username(self):
        email = self.cleaned_data.get('email')

        # Check if the username does not exist 
        if not User.objects.filter(username=email).exists():
            raise forms.ValidationError("This username does not exist.")
        
        return email
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not password:
            raise forms.ValidationError("This field is required.")
        return password
    
class UserProfileForm(forms.ModelForm):
    # all user select multiple specializations
    specializations = forms.ModelMultipleChoiceField(
        queryset=Specialization.objects.all(), 
        widget=forms.CheckboxSelectMultiple,  # Use checkboxes for multiple selection
        required=True,
    )
    class Meta:
        model = TherapistProfile
        fields = ['profile_image', 'first_name', 'last_name', 'gender', 'date_of_birth', 'country', 'bio', 'specializations', 'years_of_experience', 'languages_spoken']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),  # Use a date picker for birthdate
            'profile_image': forms.ClearableFileInput(attrs={'multiple': False})  # Keep as single file input
        }
