from django.urls import path
from . import views

app_name = 'therapy'

urlpatterns = [
    path('register/', views.registerTherapist, name='register'),
    path('verify-email/<str:uidb64>/<str:token>/', views.verify_email, name='verifyemail'),
    path('verification-pending/', views.verification_pending, name='verification_pending'),
    path('resend-verification/', views.resend_verification_link, name='resend_verification'),
    path('login/', views.LoginUser, name='login'),
    path('logout/', views.logoutUser, name='logout'), 
    path('createprofile/', views.createprofile, name='createprofile'),
    path('therapist/<int:therapist_id>/', views.therapistprofile_view, name='therapistprofile'), # therapistprofile url for request.user 
    path('editprofile/', views.edit_therapist_profile, name='editprofile'), # edit page url 
    path('<int:therapist_id>/', views.profiledetail_view, name='profiledetail'), 
]