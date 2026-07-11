
from django.db.models.signals import pre_save, post_save, pre_delete
from django.dispatch import receiver
from django.shortcuts import get_object_or_404

from apps.journals.models import Mkb10ServiceJournal
from apps.patients.models import MKB10DoctorAppointmentData, ServiceAppointmentData
from config.middleware import get_current_user


def get_title(sender, instance):
    title = None
    if sender == ServiceAppointmentData:
        title = instance.service_id
    elif sender == MKB10DoctorAppointmentData:
        title = instance.mkb10_id

    return  title

@receiver(post_save, sender=MKB10DoctorAppointmentData)
@receiver(post_save, sender=ServiceAppointmentData)
def instance_create(sender, instance,  created, **kwargs, ):
    if created:
        Mkb10ServiceJournal.objects.create(type=sender._meta.verbose_name ,action='Новый', author_id=get_current_user(),\
                                               appointment_id=instance.appointment_id, title=get_title(sender, instance), )

@receiver(pre_save, sender=MKB10DoctorAppointmentData)
@receiver(pre_save, sender=ServiceAppointmentData)
def instance_update(sender, instance, **kwargs, ):
    if instance._state.adding==False:
        if sender == ServiceAppointmentData:
            old_title = get_object_or_404(ServiceAppointmentData, pk=instance.id).service_id
            new_title =instance.service_id
            action = 'Изменена услуга'
        elif sender == MKB10DoctorAppointmentData:
            old_title = get_object_or_404(MKB10DoctorAppointmentData, pk=instance.id).mkb10_id
            new_title =instance.mkb10_id
            action = 'Изменен МКБ10'
        if old_title != new_title:
            Mkb10ServiceJournal.objects.create(type=sender._meta.verbose_name ,action=action, author_id=get_current_user(), \
                                               appointment_id=instance.appointment_id, title=old_title, title_new=new_title,)


@receiver(pre_delete, sender=MKB10DoctorAppointmentData)
@receiver(pre_delete, sender=ServiceAppointmentData)
def instance_delete(sender, instance, using, origin=None, **kwargs):
    Mkb10ServiceJournal.objects.create(type=sender._meta.verbose_name ,action='Удаление', author_id=get_current_user(),\
                                       appointment_id=instance.appointment_id, title=get_title(sender, instance), )



