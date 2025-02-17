from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .forms import EndUserProfileForm


# Create your views here.

def log_out(request):
    """Log out the current user"""

    logout(request)
    return redirect('welcome_page')


@login_required 
def profile(request):
    """View to display the user profile"""
    user = request.user

    if hasattr(user, 'User_profile'):  # Check if profile exists
        return render(request, 'Profile/show_profile.html', {'user': user.User_profile})
    else:
        messages.error(request, "User profile not found.")
        return redirect('welcome_page')  


 
@login_required  
def update_profile(request):
    """Update user profile details."""
    user = request.user  

    if not hasattr(user, 'User_profile'):
        messages.error(request, "Profile not found.")
        return redirect('welcome_page')

    if request.method == "POST":
        form = EndUserProfileForm(request.POST, instance=user.User_profile, user=user)
        if form.is_valid():
            try:
                form.save()
            except Exception:
                form.add_error(None, "An unexpected error occurred. Please try again.")
            else:
                messages.success(request, "Your profile has been updated successfully!")
                return redirect('show_profile')  
    else:
        form = EndUserProfileForm(instance=user.User_profile, user=user)

    return render(request, 'Profile/update_profile.html', {'form': form, 'user': user})



@login_required
def delete_account(request):
    """Handle both confirmation page and actual account deletion."""
    if request.method == "POST":
        user = request.user

        # Delete all related objects first
        user.User_profile.program_enrollments.all().delete()
        user.User_profile.module_enrollments.all().delete()
        user.User_profile.program_progress.all().delete()
        user.User_profile.module_progress.all().delete()

        # Delete EndUser profile first, if it exists
        end_user_profile = getattr(user, 'User_profile', None)
        if end_user_profile:
            end_user_profile.delete()
        
        # Then delete user and log them out
        user.delete()
        logout(request)
        messages.success(request, "Your account has been successfully deleted.")
        return redirect('welcome_page')

    context = {'confirmation_text': "Are you sure you want to delete your account? This action cannot be undone."}
    return render(request, 'Profile/delete_account.html', context)

