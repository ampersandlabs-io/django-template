from django.contrib import admin


# To add a profile model’s fields to the user page in the admin, define an InlineModelAdmin
# (for this example, we’ll use a StackedInline) in your app’s admin.py and add it to a UserAdmin
# class which is registered with the User class:


# class EmployeeInline(admin.StackedInline):
#     model = Employee
#     can_delete = False
#     verbose_name_plural = 'employee'
#
# # Define a new User admin
# class UserAdmin(UserAdmin):
#     inlines = (EmployeeInline, )
#
# # Re-register UserAdmin
# admin.site.unregister(User)
# admin.site.register(User, UserAdmin)