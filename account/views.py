from django.shortcuts import render, redirect
from account.forms import RegistrationForm, PasswordResetForm
from django.contrib import messages

from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse

from account.utils import send_activation_email, send_reset_password_email
from account.models import User

from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import SetPasswordForm

# Create your views here.


def home(request):
    return render(request, "account/home.html")


def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_seller:
            return redirect("seller_dashboard")
        elif request.user.is_customer:
            return redirect("customer_dashboard")
        return redirect("home")

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not email or not password:
            messages.error(request, "Both of the fields are required")
            return redirect("login")

        # This will once look up in the table and check if the user exists by comparing email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "Invalid Email or Password")
            return redirect("login")

        if not user.is_active:
            messages.error(
                request, "Your account is inactive. Please activate your account"
            )
            return redirect("login")

        # Authentication code
        # This will again look up in the table for authentication using email and password. So 2 database query runs.
        user = authenticate(request, email=email, password=password)

        # To avoid two lookups in the database, use the view in the last section for login.

        # For authenticated user:
        if user is not None:
            login(request, user)
            if user.is_seller:
                return redirect("seller_dashboard")
            elif user.is_customer:
                return redirect("customer_dashboard")
            else:
                messages.error(request, "You don't have permission to access this area")
                return redirect("home")
        else:
            messages.error(request, "Invalid email or password")
            return redirect("login")

    return render(request, "account/login.html")


def register_view(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Save the user in the database
            user = form.save(commit=False)
            print("User:\n", user.password)
            user.set_password(
                form.cleaned_data["password"]
            )  # This will save the hashed password instead of raw password
            user.is_active = False  # For security reason(already is is_active=False)
            user.save()

            # For the part of sending the activation link to user's mail
            uidb64 = urlsafe_base64_encode(
                force_bytes(user.pk)
            )  # example: MTI--representing 12 as pk as 12
            token = default_token_generator.make_token(user)
            activation_link = reverse(
                "activate", kwargs={"uidb64": uidb64, "token": token}
            )

            activation_url = f"{settings.SITE_DOMAIN}{activation_link}"

            send_activation_email(user.email, activation_url)

            messages.success(
                request,
                "Registration is successful. Please check your email to activate your account.",
            )
            return redirect("login")
    else:
        form = RegistrationForm()

    return render(request, "account/register.html", {"form": form})


# View that will be called after clicking activation link in mail
def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))

        user = User.objects.get(pk=uid)

        if user.is_active:
            messages.warning(request, "The account has already been active.")
            return redirect("login")

        # Checking if the token obtained is based on the user or not.
        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            messages.success(request, "Your account has been activated successfully!!")
            return redirect("login")
        else:
            messages.error(request, "The activation link is invalid or is expired")
            return redirect("login")
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        messages.error(request, "Invalid activation link")
        return redirect("login")


# For Forgot Password Section
def password_reset_view(request):
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            user = User.objects.filter(email=email).first()
            if user:
                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)

                reset_url = reverse(
                    "password_reset_confirm", kwargs={"uidb64": uidb64, "token": token}
                )

                # We can also do this where the site domain don't need to be mentioned
                absolute_reset_url = f"{request.build_absolute_uri(reset_url)}"
                
                # For the case the email sending limit is reached and you want to access new password setting page
                # print("Absolute Reset URL:\n")
                # print(absolute_reset_url)

                send_reset_password_email(user.email, absolute_reset_url)

            messages.success(
                request, "We have sent you a password reset link. Check in your email"
            )

            return redirect("login")
    else:
        form = PasswordResetForm()

    return render(request, "account/password_reset.html", {"form": form})


# the uidb64 and token will automatically be passed as arguments to your view function — because Django’s URL dispatcher extracts them based on your URL pattern definition.
def password_reset_confirm_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)

        if not default_token_generator.check_token(user, token):
            messages.error(request, ("This link has been expired or invalid"))
            return redirect("password_reset")

        if request.method == "POST":
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, ("Your password is successfully reset"))
                return redirect("login")
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, error)
        else:
            form = SetPasswordForm(user)

        return render(
            request,
            "account/password_reset_confirm.html",
            # {"form": form},
            {"form": form, "uidb64": uidb64, "token": token},
        )

    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        messages.error(request, ("An error occured. Please try again later."))

        return redirect("password_reset")


# Updated codes

"""
Login view
def login_view(request):
    def redirect_user(user):
        if user.is_seller:
            return redirect("seller_dashboard")
        elif user.is_customer:
            return redirect("customer_dashboard")
        return redirect("home")

    if request.user.is_authenticated:
        return redirect_user(request.user)

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not email or not password:
            messages.error(request, "Both fields are required")
            return redirect("login")

        user = authenticate(request, email=email, password=password)

        if user is not None:
            if not user.is_active:
                messages.error(
                    request, "Your account is inactive. Please activate your account."
                )
                return redirect("login")

            login(request, user)
            return redirect_user(user)

        messages.error(request, "Invalid email or password")
        return redirect("login")

    return render(request, "account/login.html")


"""
