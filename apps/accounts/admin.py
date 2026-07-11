from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.accounts.models import *

# Register your models here.

class PacientProfiletModelAdmin(admin.StackedInline):
    model = PacientProfile

class DoctorProfileModelAdmin(admin.StackedInline):
    model = DoctorProfile

@admin.register(get_user_model())
class ProjectUserModelAdmin(UserAdmin):
    list_display=('pk', 'email', 'last_name', 'first_name', 'get_date_birth', )
    fieldsets = (
        ('Fields for all users', {
            'fields': (
                'email', 'password', 'last_name', 'first_name', 'patronymic', 'phone',
                'is_active', 'is_staff', 'is_superuser', 'groups', )
        }),
    )
    add_fieldsets = (
        (None, {
            'fields': ('email', 'password1', 'password2', 'last_name', 'first_name', 'patronymic', 'phone',
                        'is_active', 'is_staff', 'is_superuser', 'groups',),
        }),
    )
    ordering = ('pk',)
    list_filter = ['email', 'last_name',]

    inlines = (PacientProfiletModelAdmin, DoctorProfileModelAdmin)

    def get_date_birth(self, obj):
        return obj.pacient_profile_user_id.date_birth

    get_date_birth.short_description = 'Дата рождения пациента'


