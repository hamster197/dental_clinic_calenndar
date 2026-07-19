from django import forms
from django.core.exceptions import ValidationError

from django.contrib.auth import get_user_model

from apps.patients.models import DoctorAppointment, MKB10DoctorAppointmentData, ServiceAppointmentData, \
    DentalFormulaAppointment
from apps.patients.utils import check_correct_patient_data_in_string, check_for_correct_user_input_with_date_birth
from datetime import datetime

class PatientForm(forms.Form):
    patient = forms.CharField(label="Выберите пациента", max_length=150, required=True, )

    def clean(self):
        cleaned_data = super().clean()
        if not check_correct_patient_data_in_string(self.cleaned_data.get('patient')):
            raise ValidationError("Введите Фамлию Имя И дату рождения в формате 1999-01-01")

        return cleaned_data


class PatientEditForm(forms.ModelForm):
    date_birth = forms.DateField(label="Дата рождения", required=True,
                                 widget=forms.DateInput(format='%Y-%m-%d',
                                                        attrs={'type': 'date', 'class': 'form-control'})
                                 )

    class Meta:
        model = get_user_model()
        fields = ['email', 'first_name', 'last_name', 'patronymic', 'phone', 'date_birth', ]

    def __init__(self, *args, **kwargs):
        date_birth = kwargs.pop("date_birth")
        super().__init__(*args, **kwargs)
        self.fields['date_birth'].initial = date_birth

    def clean(self):
        cleaned_data = super(PatientEditForm, self).clean()
        pk = None
        if self.instance:
            pk = self.instance.pk
        first_name = cleaned_data['first_name']
        last_name = cleaned_data['last_name']
        date_birth = cleaned_data['date_birth']

        if check_for_correct_user_input_with_date_birth(first_name, last_name, date_birth, pk):
            raise ValidationError('Пользователь с данным ФИО и датой рождения уже зарегестрирован!', code='invalid')

        return cleaned_data

class AppointmentForm(forms.ModelForm):

    @property
    def model_verbose_name(self):
        return self._meta.model._meta.verbose_name

    @property
    def model_name(self):
        return self._meta.model.__name__

class AppointmentTextForm(AppointmentForm):

    class Meta:
        model = DoctorAppointment
        fields = ['recomendations', 'text',]


class MKB10DoctorAppointmentDataForm(AppointmentForm):

    class Meta:
        model = MKB10DoctorAppointmentData
        fields = ['mkb10_id', ]

    def __init__(self, *args, **kwargs,):
        qst = kwargs.pop('qst', None)
        super().__init__(*args, **kwargs)
        self.fields['mkb10_id'].queryset = qst

class ServiceAppointmentDataForm(AppointmentForm):
    # date_time = forms.DateTimeField(
    #     widget=forms.DateTimeInput(
    #         format='%Y-%m-%dT%H:%M',
    #         attrs={'type': 'datetime-local'}
    #     ),
    #     input_formats=['%Y-%m-%dT%H:%M']
    # )
    date_time = forms.SplitDateTimeField(
        widget=forms.SplitDateTimeWidget(
            date_attrs={'type': 'date'},
            date_format='%Y-%m-%d',
            time_attrs={'type': 'time'}
        )
    )

    class Meta:
        model = ServiceAppointmentData
        fields = ['service_id', 'doctor_id', 'date_time', 'status',]

    def __init__(self, *args, **kwargs,):
        user_id = kwargs.pop('user_id', None)
        super().__init__(*args, **kwargs)
        self.fields['doctor_id'].queryset = get_user_model().objects.filter(groups__name="Врач")
        self.fields['doctor_id'].initial = user_id
        self.fields['date_time'].initial = datetime.now()


class ServiceAppointmentCreateForm(ServiceAppointmentDataForm):

    class Meta(ServiceAppointmentDataForm.Meta):
        fields = ['service_id', 'doctor_id', 'date_time', ]

    def clean(self):
        cleaned_data = super(ServiceAppointmentCreateForm, self).clean()
        from django.utils import timezone
        if cleaned_data['date_time'] < timezone.now().astimezone():
            raise ValidationError('Дата и время меньше сейчас!', code='invalid')

        return cleaned_data


class DentalFormulaAppointmentForm(AppointmentForm):

    class Meta:
        model = DentalFormulaAppointment
        fields = ['comment', ]
