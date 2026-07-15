from django.contrib.auth import get_user_model
from django.db.models import Q, Subquery, OuterRef, Count, Sum, PositiveIntegerField
from django.db.models.functions import Coalesce
from datetime import datetime, timedelta

from apps.accounts.models import PacientProfile, User
from apps.guides.constants import ToothChoises
from apps.guides.models import MKB10Quide
from apps.patients.models import DoctorAppointment, ServiceAppointmentData, MKB10DoctorAppointmentData, \
    DoctorAppointmentFile


def is_valid_date(date_string, date_format="%Y-%m-%d"):
    try:
        datetime.strptime(date_string, date_format)
        return True
    except ValueError:
        return False

def check_correct_patient_data_in_string(txt):
    result = True
    if txt:
        data = txt.split()
        if len(data) != 3:
            result = False
        else:
            import re
            date = re.findall(r'\d{4}-\d{2}-\d{2}',  data[2])
            if len(date) != 1 or len(data[0]) == 1 or len(data[1]) == 1 or len(data[2]) != 10 or not is_valid_date(data[2]):
                result = False
    else:
        result = False

    return result

def get_all_patients():
    return PacientProfile.objects.filter(user_id__groups__name='Пациент').prefetch_related('user_id')

def get_a_patient(txt):
    patient_pk = None
    data = txt.split()
    if len(data) == 3:
        object_list = User.objects.filter(Q(last_name=data[0], first_name=data[1], pacient_profile_user_id__date_birth=data[2]) | \
                                          Q(last_name=data[1], first_name=data[0], pacient_profile_user_id__date_birth=data[2]))
        if object_list.exists():
            patient_pk = object_list.first().pk

    return patient_pk

def check_for_correct_user_input_with_date_birth(first_name, last_name, date_birth, pk=None):
    if pk:
        users = get_user_model().objects.filter(first_name=first_name, last_name=last_name, pacient_profile_user_id__date_birth=date_birth,).exclude(pk=pk)
    else:
        users = get_user_model().objects.filter(first_name=first_name, last_name=last_name, pacient_profile_user_id__date_birth=date_birth,)

    return users.exists()

def create_or_update_pacient_profile(user_id, date_birth):
    PacientProfile.objects.update_or_create(
        user_id=user_id, defaults={"date_birth": date_birth} )

def appointments_list_with_counts(appointments_id):
    queryset = DoctorAppointment.objects.filter(patient_id=appointments_id).annotate(
        service_sum = Coalesce(Subquery(
            ServiceAppointmentData.objects.filter(appointment_id=OuterRef('pk'))
            .values('appointment_id')
            .annotate(service_sum=Count('pk'))
            .values('service_sum')
        ),0),
        mkb10_sum = Coalesce(Subquery(
            MKB10DoctorAppointmentData.objects.filter(appointment_id=OuterRef('pk'))
            .values('appointment_id')
            .annotate(mkb10_sum=Count('pk'))
            .values('mkb10_sum')
        ),0),
        total_sum = Coalesce(Subquery(
        ServiceAppointmentData.objects.filter(appointment_id=OuterRef('pk'))
        .values('appointment_id')
        .annotate(total_sum=Sum('service_id__price_base'))
        .values('total_sum')
        ),0),
        payed = Coalesce(Subquery(
            ServiceAppointmentData.objects.filter(appointment_id=OuterRef('pk'))
            .values('appointment_id')
            .annotate(payed=Coalesce(Sum('service_id__price_base', filter=Q(status=True)), 0,
                                     output_field=PositiveIntegerField(),),)
            .values('payed')
        ),0),
        debt = Coalesce(Subquery(
            ServiceAppointmentData.objects.filter(appointment_id=OuterRef('pk'))
            .values('appointment_id')
            .annotate(debt=Coalesce(Sum('service_id__price_base', filter=Q(status=False)), 0,
                                     output_field=PositiveIntegerField(),),)
            .values('debt')
        ),0),
    ).values('date_created', 'pk','service_sum' ,'mkb10_sum', 'total_sum', 'payed', 'debt',)

    return queryset


def save_images_from_post(object, files):
    new_pictures_in_galery = []
    for file in files:
        new_pictures_in_galery.append(DoctorAppointmentFile(parent_id=object , file=file))

    DoctorAppointmentFile.objects.bulk_create(new_pictures_in_galery)

def get_appointment_pay_sum(appointment):
    qst = appointment.patients_serviceappointmentdata.all().aggregate(
                                        total_sum=Sum('service_id__price_base'),
                                        payed = Coalesce(Sum('service_id__price_base',
                                            filter=Q(status=True)), 0, output_field=PositiveIntegerField(),),
                                        debt = Coalesce(Sum('service_id__price_base',
                                            filter=Q(status=False)), 0, output_field=PositiveIntegerField(),),
                                        )

    return qst

def get_user_appointment_create_mkb_qst(appointment):
    to_exclude = appointment.patients_mkb10doctorappointmentdata.all().values_list('mkb10_id__id')
    qst = MKB10Quide.objects.exclude(id__in=to_exclude).order_by('code')

    return qst

def get_user_appointment_update_mkb_qst(appointment):
    to_exclude = (MKB10DoctorAppointmentData.objects.filter(appointment_id=appointment.appointment_id)
                  .exclude(mkb10_id=appointment.mkb10_id).values_list('mkb10_id__id'))
    qst = MKB10Quide.objects.exclude(id__in=to_exclude)

    return qst

def get_appointment_by_pk(pk):
    return DoctorAppointment.objects.get(pk=pk)

def get_calendar_week_days(date_now, user_id):
    day_of_week = date_now.weekday()
    start_of_week = date_now - timedelta(days=day_of_week)
    dates = [start_of_week + timedelta(days=i) for i in range(7)]
    queryset = ServiceAppointmentData.objects.filter(date_time__date__gte=dates[0], date_time__date__lte=dates[6], doctor_id=user_id,)

    return dates, queryset

def get_calendar_week_days_qst(qst, day_of_week):
    monday_qst = qst.filter(date_time__date=day_of_week[0])
    tuesday_qst = qst.filter(date_time__date=day_of_week[1])
    wednesday_qst = qst.filter(date_time__date=day_of_week[2])
    thursday_qst = qst.filter(date_time__date=day_of_week[3])
    friday_qst = qst.filter(date_time__date=day_of_week[4])
    saturday_qst = qst.filter(date_time__date=day_of_week[5])
    sunday_qst = qst.filter(date_time__date=day_of_week[6])

    return monday_qst, tuesday_qst, wednesday_qst, thursday_qst, friday_qst, saturday_qst, sunday_qst

def get_dental_formula(obj):
    qst = obj.dental_formula_appointment_id.all().select_related('dental_formula_id', 'author_id',)

    return qst.filter(dental_formula_id__position_vertical=ToothChoises.Up),  qst.filter(dental_formula_id__position_vertical=ToothChoises.Down)