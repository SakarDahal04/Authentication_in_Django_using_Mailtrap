from django.shortcuts import render, redirect
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required


# Create your views here.
@login_required
def customer_dashboard_view(request):
    return render(request, "customer/dashboard.html")

@login_required
def password_change_view(request):
    if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            logout(request)
            messages.success(request, "Password Changed Successfully. Please login with new password")
            return redirect('login')
        else:
            # Handle form errors and display to user
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, "customer/password_change.html", {'form': form})
