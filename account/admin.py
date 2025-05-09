from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from account.models import User

# Register your models here.
class UserModelAdmin(UserAdmin):
    model = User

    # We set the required fields that we need to be shown in the User model
    # This overrides the definition on the base UserModelAdmin i.e UserAdmin that we inherited that reference to the specific fields on auth.User
    # This means that instead of the fields that were shown when creating auth.User model, we will show the fields that we want to User model that we created to see.
    
    list_display = ['id', 'email', 'name', 'is_active', 'is_superuser', 'is_staff', 'is_customer', 'is_seller']

    # We can filter these fields based on the superuser.
    list_filter = ['is_superuser']
    
    # We can show the content on the basis of the category
    # That means the category that we defined can be used for showing the User table content
    # This will divide the model content in the sections when we click on specific content
    fieldsets = [
        ('User Credentials', {"fields": ["email", "password"]}),
        ('Personal Information', {"fields": ["name", "city"]}),
        ('Permissions', {"fields": ["is_active", "is_staff", "is_superuser", "is_customer", "is_seller"]})
    ]

    # add_fieldsets is not a standard ModelAdmin attribute.
    # UserModelAdmin overrides the get_fieldsets to use this attribute when creating a user
    # add_fieldsets is list of tuples. Each tuples represents a section in the Add User form
    
    # So when we add the user, what are the fields that are to be shown in form.
    # Here when a using is being created via admin panel, we would ask for the email, password1 and password2 fields.s

    # If we want the city to be shown or any other fields to be shown when adding content via admin panel then we need to add that to the fields. Like if we want to add city ==> 
    # "fields" : ["email", "password1", "password2", "city"]
    add_fieldsets = [
        (
            # it is title of the section and setting it to None leaves the section title blank 
            None,
            {
                # It is css class to make full width admin layout
                "classes": ["wide"],
                # This fields will appear in admin panel add user form
                "fields": ['email', 'password1', 'password2']
            }
        )
    ]
    
    search_fields = ["email"]
    ordering = ["email", "id"]
    filter_horizontal = []

# finally regiter the new UserModelAdmin

admin.site.register(User, UserModelAdmin)
