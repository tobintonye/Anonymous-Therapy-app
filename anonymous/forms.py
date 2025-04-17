from django import forms
from django.contrib.auth.forms import UserCreationForm
import uuid
from django.contrib.auth import get_user_model

User = get_user_model()

# register anonymous userform
class AnonymousUserForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email'}))
    password1 = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'password'}))
    password2 = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'confirm password'}))

    class Meta:
        model = User
        fields = ["email", "password1", "password2"]  # No need for username, it's generated for anonymous users
    def save(self, commit=True):
        user = super().save(commit=False)
        # Ensure username is generated for anonymous users
        if user.role == User.UserRole.ANONYMOUS_USER:
            user.username = f"anon_{uuid.uuid4().hex[:8]}"
        if commit:
            user.save()
        return user
    
# login form
class LoginForm(forms.Form):
    email = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'email'}))
    password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    remember_me = forms.BooleanField(required=False, initial=False, widget=forms.CheckboxInput())

    # check if email exist
    def clean_email(self):
        email = self.cleaned_data.get('email')

        # Check if the username does not exist 
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address does not exist.")
        return email
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not password:
            raise forms.ValidationError("This field is required.")
        return password