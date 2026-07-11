from django.contrib import admin

from apps.journals.models import *

# Register your models here.
@admin.register(Mkb10ServiceJournal)
class Mkb10ServiceJournaltModelAdmin(admin.ModelAdmin):
    list_display = [ 'creation_date', 'type', 'action', 'appointment_id', 'title', 'title_new', ]
    list_filter = ['appointment_id__date_created',  'appointment_id__patient_id__last_name', ]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
