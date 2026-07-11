from django.urls import path

from apps.patients.forms import AppointmentTextForm, MKB10DoctorAppointmentDataForm, ServiceAppointmentDataForm, \
    DentalFormulaAppointmentForm
from apps.patients.models import DoctorAppointmentFile, DoctorAppointment, MKB10DoctorAppointmentData, \
    ServiceAppointmentData, DentalFormulaAppointment
from apps.patients.views import PatientChoiseView, PatientDetailView, PatientCreateView, PatientUpdateView, \
    AppointmentUpdatelView, AppointmentFormView, DoctorAppointmentInstancesDeleteView, AppointmentCreateView, \
    NewApointmentVew, DoctorJournalView, ServiceDetailView

app_name = 'patients_urls'

urlpatterns = [
    path('patient_choise/', PatientChoiseView.as_view(), name='patient_choise_url'),
    path('patient_create/', PatientCreateView.as_view(), name='patient_create_url'),
    path('update/<int:pk>/', PatientUpdateView.as_view(), name='patient_update_url'),
    path('<int:pk>/', PatientDetailView.as_view(), name='patient_detail_url'),

    path('appointment/<int:pk>/', AppointmentUpdatelView.as_view(), name='appointment_update_url'),
    path('appointment/new/<int:pk>/', NewApointmentVew.as_view(), name='appointment_new_url'),
    # Updates
    path('appointment/text/<int:pk>/', AppointmentFormView.as_view(form_class=AppointmentTextForm, model=DoctorAppointment), name='appointment_text_url'),
    path('appointment/mkb10/<uuid:pk>/', AppointmentFormView.as_view(form_class=MKB10DoctorAppointmentDataForm, model=MKB10DoctorAppointmentData), name='appointment_mkb10_url'),
    path('appointment/service/<uuid:pk>/', AppointmentFormView.as_view(form_class=ServiceAppointmentDataForm, model=ServiceAppointmentData), name='appointment_service_url'),
    path('appointment/dental_formula/<int:pk>/', AppointmentFormView.as_view(form_class=DentalFormulaAppointmentForm, model=DentalFormulaAppointment), name='appointment_dental_formula_url'),
    # Deletes
    path('appointment/galery_delete/<uuid:pk>/', DoctorAppointmentInstancesDeleteView.as_view(model=DoctorAppointmentFile), name='appointment_galery_delete_url'),
    path('appointment/mkb10_delete/<uuid:pk>/', DoctorAppointmentInstancesDeleteView.as_view(model=MKB10DoctorAppointmentData), name='appointment_mkb10_delete_url'),
    path('appointment/service_delete/<uuid:pk>/', DoctorAppointmentInstancesDeleteView.as_view(model=ServiceAppointmentData), name='appointment_service_delete_url'),
    # Creates
    path('appointment/mkb10_create/<int:pk>/', AppointmentCreateView.as_view(form_class=MKB10DoctorAppointmentDataForm, model=MKB10DoctorAppointmentData), name='appointment_mkb10_create_url'),
    path('appointment/service_create/<int:pk>/', AppointmentCreateView.as_view(form_class=ServiceAppointmentDataForm, model=ServiceAppointmentData), name='appointment_service_create_url'),
    # Logs
    path('logs/mkb/<int:pk>/', DoctorJournalView.as_view(type='mkb10'), name='logs_mkb_url'),
    path('logs/service/<int:pk>/', DoctorJournalView.as_view(type='service'), name='logs_services_url'),

    # path('calendar/', CalendarView.as_view(), name='calendar_url'),
    path('appointment/service_detail/<uuid:pk>/', ServiceDetailView.as_view(), name='appointment_service_detail_url'),

]