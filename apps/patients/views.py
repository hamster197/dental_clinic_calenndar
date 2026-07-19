from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView, RedirectView
from django.core.cache import cache
from django.contrib import messages
from datetime import datetime

from apps.accounts.models import User
from apps.journals.models import Mkb10ServiceJournal
from apps.patients.forms import PatientForm, PatientEditForm, AppointmentTextForm, MKB10DoctorAppointmentDataForm, \
    ServiceAppointmentDataForm, DentalFormulaAppointmentForm, ServiceAppointmentCreateForm
from apps.patients.models import DoctorAppointment, ServiceAppointmentData, \
    MKB10DoctorAppointmentData
from apps.patients.utils import get_all_patients, get_a_patient, create_or_update_pacient_profile, \
    appointments_list_with_counts, save_images_from_post, get_appointment_pay_sum, get_user_appointment_create_mkb_qst, \
    get_user_appointment_update_mkb_qst, get_appointment_by_pk, get_calendar_week_days, get_dental_formula, \
    get_calendar_week_days_qst
from config.mixins import DoctorExistsMixin
from config.settings import DOCTOR_BREADCRUMBS_URL


class PatientChoiseView(DoctorExistsMixin, ListView):
    template_name = 'patients/patient_choise.html'
    context_object_name = 'patients'

    def get_queryset(self):
        return get_all_patients()

    def get_breadcrumbs(self):
        crumbs = []
        crumbs.append({'title': 'Главаная(каледарь)',  'url': DOCTOR_BREADCRUMBS_URL})
        crumbs.append({'title': 'Прием пациента',  'url': reverse_lazy('patients_urls:patient_choise_url')})

        return crumbs

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PatientForm
        context['breadcrumbs'] = self.get_breadcrumbs()

        return context

    def post(self, request, *args, **kwargs):
        form = PatientForm(request.POST)
        if form.is_valid():
            txt = form.cleaned_data['patient']
            patient_pk = get_a_patient(txt)
            if patient_pk is not None:
                return redirect('patients_urls:patient_detail_url', pk=patient_pk)
            else:
                cache_key = f"user_profile_data_{request.user.id}"
                cache.set(cache_key, txt.split(), timeout=9)
                return redirect('patients_urls:patient_create_url', )

        return render(request, self.template_name, {'form':form, 'patients':self.get_queryset()})

class PatientDetailView(DoctorExistsMixin, DetailView):
    template_name = 'patients/patient_detail.html'
    model = get_user_model()
    context_object_name = 'patient'

    def get_breadcrumbs(self):
        crumbs = []
        crumbs.append({'title': 'Главаная(каледарь)',  'url': DOCTOR_BREADCRUMBS_URL})
        crumbs.append({'title': 'Прием пациента',  'url': reverse_lazy('patients_urls:patient_choise_url')})
        name = self.object.first_name + ' ' + self.object.last_name
        crumbs.append({'title': name,  'url': reverse_lazy('patients_urls:patient_detail_url', kwargs={'pk': self.object.pk})})

        return crumbs

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = self.get_breadcrumbs()
        context['appointments'] = appointments_list_with_counts(self.kwargs['pk'])

        return context

class PatientCreateView(DoctorExistsMixin, CreateView):
    template_name = 'patients/patient_update.html'
    first_name = None
    last_name = None
    email = None
    model = get_user_model()
    form_class = PatientEditForm

    def get_breadcrumbs(self):
        crumbs = []
        crumbs.append({'title': 'Главаная(каледарь)',  'url': DOCTOR_BREADCRUMBS_URL})
        crumbs.append({'title': 'Прием пациента',  'url': reverse_lazy('patients_urls:patient_choise_url')})

        return crumbs

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = self.get_breadcrumbs()

        return context

    def get_data_from_cache(self):
        cache_key = f"user_profile_data_{self.request.user.id}"
        return cache.get(cache_key, )

    def get_initial(self):
        initial = super().initial.copy()
        data = self.get_data_from_cache()
        if data is not None:
            initial['first_name'] = data[1]
            initial['last_name'] = data[0]

        return initial
    #
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        data = self.get_data_from_cache()
        if data:
            kwargs.update({'date_birth': data[2] })
        else:
            kwargs.update({'date_birth': '' })

        return kwargs

    def form_valid(self, form):
        super().form_valid(form)
        create_or_update_pacient_profile(self.object, form.cleaned_data['date_birth'])
        messages.success(self.request, 'Данные успешно сохранины!')

        return super().form_valid(form)

    def get_success_url(self, ):
        return reverse_lazy('patients_urls:patient_detail_url', kwargs={'pk':self.object.pk})

class PatientUpdateView(DoctorExistsMixin, UpdateView):
    template_name = 'patients/patient_update.html'
    model = get_user_model()
    form_class = PatientEditForm

    def get_breadcrumbs(self):
        crumbs = []
        crumbs.append({'title': 'Главаная(каледарь)',  'url': DOCTOR_BREADCRUMBS_URL})
        crumbs.append({'title': 'Прием пациента',  'url': reverse_lazy('patients_urls:patient_choise_url')})
        name = self.object.first_name + ' ' + self.object.last_name
        crumbs.append({'title': name,  'url': reverse_lazy('patients_urls:patient_detail_url', kwargs={'pk': self.object.pk})})
        crumbs.append({'title': 'Редактор профиля',  'url': reverse_lazy('patients_urls:patient_update_url', kwargs={'pk': self.object.pk})})

        return crumbs

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs_title'] = 'patient_update'
        context['breadcrumbs'] = self.get_breadcrumbs()

        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'date_birth': self.object.pacient_profile_user_id.date_birth })

        return kwargs

    def form_valid(self, form):
        create_or_update_pacient_profile(self.object, form.cleaned_data['date_birth'])
        messages.success(self.request, 'Данные успешно изменены!')

        return super().form_valid(form)

    def get_success_url(self, ):
        return reverse_lazy('patients_urls:patient_update_url', kwargs={'pk':self.object.pk})

class AppointmentUpdatelView(DoctorExistsMixin, DetailView):
    model = DoctorAppointment
    template_name = 'patients/appointment_detail.html'
    model = DoctorAppointment
    context_object_name = 'instance'

    def get_breadcrumbs(self):
        crumbs = []
        crumbs.append({'title': 'Главаная(каледарь)',  'url': DOCTOR_BREADCRUMBS_URL})
        crumbs.append({'title': 'Прием пациента',  'url': reverse_lazy('patients_urls:patient_choise_url')})
        name = self.object.patient_id.first_name + ' ' + self.object.patient_id.last_name
        crumbs.append({'title': name,  'url': reverse_lazy('patients_urls:patient_detail_url', kwargs={'pk': self.object.patient_id.pk})})
        crumbs.append({'title': 'Редактор посешения',  'url': reverse_lazy('patients_urls:appointment_update_url', kwargs={'pk': self.object.pk})})

        return crumbs

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = self.get_breadcrumbs()
        context['appointment_sum'] = get_appointment_pay_sum(self.get_object())
        context['dental_formula_up'], context['dental_formula_down'] = get_dental_formula(self.object)

        return context

    def post(self, request, *args, **kwargs):
        save_images_from_post(self.get_object(), self.request.FILES.getlist('images'))
        messages.success(self.request, 'Изображения успешно загружены!')

        return redirect('patients_urls:appointment_update_url', pk=self.get_object().pk)

class DoctorAppointmentInstancesDeleteView(DoctorExistsMixin, DeleteView):
    model = None
    template_name = 'patients/confirm_delete.html'
    pk_url_kwarg = 'pk'

    def get_queryset(self):
        if self.model == ServiceAppointmentData:
            qst = self.model.objects.filter(status=False)
        else:
            qst = self.model.objects.all()

        return qst

    def get_success_url(self, ):
        messages.success(self.request, 'Данные успешно уделены!')
        if 'File' in str(self.model):
            url = reverse_lazy('patients_urls:appointment_update_url', kwargs={'pk':self.object.parent_id.pk})
        else:
            url = reverse_lazy('patients_urls:appointment_update_url', kwargs={'pk':self.object.appointment_id.pk})

        return url

class AppointmentFormView(DoctorExistsMixin, UpdateView):
    template_name = 'patients/appointment_update.html'
    model = form_class = None

    def get_queryset(self):
        if self.model == ServiceAppointmentData:
            qst = self.model.objects.filter(status=False)
        else:
            qst = self.model.objects.all()

        return qst


    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.model == MKB10DoctorAppointmentData:
            kwargs.update({'qst': get_user_appointment_update_mkb_qst(self.object) })

        return kwargs

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['appointment__title'] = 'appointment_update'

        return context

    def form_valid(self, form):
        obj = form.save(commit=False)
        if self.form_class == DentalFormulaAppointmentForm:
            obj.author_id =self.request.user

        obj.save()

        return super().form_valid(form)

    def get_success_url(self, ):
        messages.success(self.request, 'Данные успешно изменены!')
        if self.form_class == AppointmentTextForm:
            url = reverse_lazy('patients_urls:appointment_text_url', kwargs={'pk':self.object.pk})
        elif self.form_class == MKB10DoctorAppointmentDataForm:
            url = reverse_lazy('patients_urls:appointment_mkb10_url', kwargs={'pk':self.object.pk})
        elif self.form_class == ServiceAppointmentDataForm:
            if self.object.status:
                url =  reverse_lazy('patients_urls:appointment_update_url', kwargs={'pk':self.object.appointment_id.pk})
            else:
                url = reverse_lazy('patients_urls:appointment_service_url', kwargs={'pk':self.object.pk})
        elif self.form_class == DentalFormulaAppointmentForm:
            url = reverse_lazy('patients_urls:appointment_dental_formula_url', kwargs={'pk':self.object.pk})

        return url

class AppointmentCreateView(DoctorExistsMixin, CreateView):
    template_name = 'patients/appointment_update.html'
    model = form_class = None

    def dispatch(self, request, *args, **kwargs):
        self.appointment = get_appointment_by_pk(self.kwargs['pk'])

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['appointment__title'] = 'appointment_create'
        context['appointment'] = self.appointment

        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.form_class == ServiceAppointmentDataForm:
            kwargs['user_id'] = self.request.user
        if self.model == MKB10DoctorAppointmentData:
            kwargs.update({'qst': get_user_appointment_create_mkb_qst(self.appointment)})

        return kwargs

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.author_id = self.request.user
        instance.appointment_id = self.appointment

        try:
            instance.full_clean()
            instance.save()

            return redirect(self.get_success_url(instance))

        except ValidationError as e:
            form.add_error(None, e)

            return super().form_invalid(form)

    def get_success_url(self, instance):
        messages.success(self.request, 'Данные успешно сохранены!')
        if self.form_class == MKB10DoctorAppointmentDataForm:
            url = reverse_lazy('patients_urls:appointment_mkb10_url', kwargs={'pk':instance.id})
        elif self.form_class == ServiceAppointmentCreateForm:
            url = reverse_lazy('patients_urls:appointment_service_url', kwargs={'pk':instance.id })

        return url

class NewApointmentVew(DoctorExistsMixin, RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        from datetime import datetime
        today = datetime.today().date()
        patient = User.objects.get(pk=self.kwargs['pk'])
        obj = DoctorAppointment.objects.filter(date_created=today, patient_id=patient)
        if obj.exists():
            appointment = obj.first()
        else:
            appointment = DoctorAppointment.objects.create(date_created=today, author_id=self.request.user,
                                                                  patient_id=patient)

        return reverse_lazy('patients_urls:appointment_update_url', kwargs={'pk':appointment.id })

class DoctorJournalView(DoctorExistsMixin, ListView):
    type = None
    context_object_name = 'instances'
    template_name = 'patients/logs_journal.html'

    def dispatch(self, request, *args, **kwargs):
        self.appointment =  get_appointment_by_pk(kwargs['pk'])

        return super().dispatch(request, *args, **kwargs)

    def get_breadcrumbs(self):
        crumbs = []
        crumbs.append({'title': 'Главаная(каледарь)',  'url': DOCTOR_BREADCRUMBS_URL})
        crumbs.append({'title': 'Прием пациента',  'url': reverse_lazy('patients_urls:patient_choise_url')})
        name = self.appointment.patient_id.first_name + ' ' + self.appointment.patient_id.last_name
        crumbs.append({'title': name,  'url': reverse_lazy('patients_urls:patient_detail_url', kwargs={'pk': self.appointment.patient_id.pk})})
        crumbs.append({'title': 'Редактор посешения',  'url': reverse_lazy('patients_urls:appointment_update_url', kwargs={'pk': self.appointment.pk})})

        return crumbs

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = self.get_breadcrumbs()
        context['instance'] = self.appointment

        return context

    def get_queryset(self):
        qst = Mkb10ServiceJournal.objects.filter(appointment_id=self.appointment,)
        if self.type == 'mkb10':
            qst = qst.filter(type='МКБ10')
        else:
            qst = qst.filter(type='Услуга')

        return qst


class CalendarView(DoctorExistsMixin, ListView):
    model = ServiceAppointmentData
    template_name = 'patients/services_calendar.html'
    context_object_name = 'services'
    now = None
    week_days = None

    def get_queryset(self):
        search_query = self.request.GET.get('search')
        if search_query:
            self.now = datetime.fromisoformat(search_query)
        else:
            self.now = datetime.now().date()

        self.week_days, queryset = get_calendar_week_days(self.now, self.request.user)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'search' in self.request.GET:
            context['search_val'] = self.request.GET.get('search', '')
        else:
            context['search_val'] = str(self.now)

        context['monday_date'] = self.week_days[0]
        context['tuesday_date'] = self.week_days[1]
        context['wednesday_date'] = self.week_days[2]
        context['thursday_date'] =self.week_days[3]
        context['friday_date'] = self.week_days[4]
        context['saturday_date'] = self.week_days[5]
        context['sunday_date'] = self.week_days[6]
        (context['monday_qst'], context['tuesday_qst'], context['wednesday_qst'], context['thursday_qst'],
         context['friday_qst'], context['saturday_qst'], context['sunday_qst']) = get_calendar_week_days_qst(self.get_queryset(), self.week_days)

        return context

class ServiceDetailView(DoctorExistsMixin, DetailView):
    model = ServiceAppointmentData
    template_name = 'patients/services_detail.html'
    context_object_name = 'service'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['dental_formula_up'], context['dental_formula_down'] = get_dental_formula(self.object.appointment_id)

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.status = True
        self.object.save()
        context = self.get_context_data(object=self.object)
        messages.success(self.request, 'Данные успешно сохранины!')

        return self.render_to_response(context)


class BusyWindowsListJsonView(DoctorExistsMixin, ListView):

    def get_queryset(self):
        return ServiceAppointmentData.objects.filter(status=False, doctor_id=self.kwargs['doctor_id'],
                                                     date_time__date=self.kwargs['date'],)

    def render_to_response(self, context, **response_kwargs):
        queryset = self.get_queryset().values('date_time', 'date_end', )
        data = list(queryset)

        return JsonResponse(data, safe=False)

class DoctorBusyWindowsListJsonView(DoctorExistsMixin, ListView):

    def get_queryset(self):
        return ServiceAppointmentData.objects.filter(status=False, doctor_id=self.kwargs['doctor_id'], )

    def render_to_response(self, context, **response_kwargs):
        queryset = self.get_queryset().values('date_time', 'date_end', )
        data = list(queryset)

        return JsonResponse(data, safe=False)