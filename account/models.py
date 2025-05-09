from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, AbstractUser

from django.contrib.auth.models import User


class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        # Create and save the user with the given email and password
        if not email:
            raise ValueError("User must have a valid email address")
        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)
        return user

    # When we create a superuser,the User model that we defined will be referenced and then set is_staff and is_superuser to be true
    # Here **extra_fields are other fields of model for which manager is defined. For here -- name, city, is_staff, is_superuser, is_customer, is_seller, created_at, updated_at. This means other fields than the fields that wementioned. i.e email and password
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        
        if(extra_fields).get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')

        if(extra_fields).get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')

        # Creates and saves the superuser with the given email and password
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.is_customer = True
        user.is_seller = True

        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    email = models.EmailField(verbose_name="Email", max_length=255, unique=True)
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=255)

    # from this we will see which use has done the account activation through email
    is_active = models.BooleanField(default=False)

    # to allow the user for admin login or not
    is_staff = models.BooleanField(default=False)

    # to allow if the user registering can be superuser or not(we won't allow this)
    is_superuser = models.BooleanField(default=False)

    is_customer = models.BooleanField(default=True)
    is_seller = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    # Settings the field while creating the user
    USERNAME_FIELD = "email"
    
    # Changing the manager for carrying out ORM operations
    objects = UserManager()

    def __str__(self):
        return self.email

    # This is used to check if the user has specific permissions
    def has_perm(self, perm, obj=None):
        """Does the user have a specific permission"""
        # Only superuser will have permission for all the access
        return self.is_superuser

    # To check whether the user has the permission for specific app
    def has_module_perms(self, app_label):
        """Does the user have the permission to view the app `app label`?"""
        return self.is_superuser
