from django.contrib import admin

from apps.patients.models import *

# Register your models here.
class DoctorAppointmentFileModelAdmin(admin.StackedInline):
    model = DoctorAppointmentFile

class MKB10DoctorAppointmentDataModelAdmin(admin.StackedInline):
    model = MKB10DoctorAppointmentData

class ServiceAppointmentDataaModelAdmin(admin.StackedInline):
    model = ServiceAppointmentData

class DentalFormulaAppointmentModelAdmin(admin.StackedInline):
    model = DentalFormulaAppointment

@admin.register(DoctorAppointment)
class DoctorAppointmentModelAdmin(admin.ModelAdmin):
    list_display = [ 'pk', 'date_created', 'author_id', 'patient_id',]
    list_filter = ['author_id',  'patient_id', ]
    inlines = [DoctorAppointmentFileModelAdmin, MKB10DoctorAppointmentDataModelAdmin,
               ServiceAppointmentDataaModelAdmin, DentalFormulaAppointmentModelAdmin ]#,
