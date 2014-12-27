from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import Q
from django.contrib.auth.models import User

# To add a profile model's fields to the user page in the admin, define an InlineModelAdmin
# (for this example, we'll use a StackedInline) in your app's admin.py and add it to a UserAdmin
# class which is registered with the User class:

# from {{project_name}}.apps.users.models import Staff


# class StaffAdmin(UserAdmin):
#
#     def get_queryset(self, request):
#         qs = super(UserAdmin, self).get_queryset(request)
#         qs = qs.filter(Q(is_staff=True) | Q(is_superuser=True))
#         return qs
#
#     def save_model(self, request, obj, form, change):
#         if request.user.is_superuser:
#             obj.is_staff = True
#             obj.save()


# # Re-register UserAdmin
# admin.site.unregister(User)
# admin.site.register(Staff, StaffAdmin)