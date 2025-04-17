from django.urls import path, include
from . import views

app_name = 'anonymous'

urlpatterns = [
    path('signup/', views.register_anonymoususer, name='anonymoususer_signup'),
    path('verify-email/<str:uidb64>/<str:token>/', views.verify_email, name='verifyemail'),
    path('verification-pending/', views.verification_pending, name='verification_pending'),
    path('resend-verification/', views.resend_verification_link, name='resend_verification'),
    path('login/', views.login_anonymoususer, name='anonymoususer_login'),
    path('logout/', views.logoutUser, name='logout'),
]