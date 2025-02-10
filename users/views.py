from django.shortcuts import render, redirect
from django.http import Http404
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .forms import UserProfileForm
from .models import User

# Create your views here.

def log_out(request):
    """Log out the current user"""

    logout(request)
    return redirect('welcome_page')

@login_required
def profile(request):
    """View to display the user profile"""

    return render(request, 'Profile/show_profile.html', {'user': request.user})

@login_required  
def update_profile(request):
    """Update user profile details."""
    user = request.user  # Use request.user instead of querying again

    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            try:
                form.save()
            except Exception as e:
                form.add_error(None, f"An error occurred while updating your profile: {e}")
            else:
                messages.success(request, "Your profile has been updated successfully!")
                return redirect('show_profile')  
    else:
        form = UserProfileForm(instance=user)

    return render(request, 'Profile/update_profile.html', {'form': form, 'user': user})

@login_required  
def delete_account(request):
    """Handle both confirmation page and actual account deletion."""
    if request.method == "POST":
        # Delete user first, then log them out
        request.user.delete()
        logout(request)
        messages.success(request, "Your account has been successfully deleted.")
        return redirect('welcome_page')  # Redirect to homepage

    # Show confirmation page for GET requests
    context = {'confirmation_text': "Are you sure you want to delete your account? This action cannot be undone."}
    return render(request, 'Profile/delete_account.html', context)

