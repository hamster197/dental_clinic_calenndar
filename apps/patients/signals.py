from django.db.models.signals import post_delete
from django.dispatch import receiver

from apps.patients.models import DoctorAppointmentFile


@receiver(post_delete, sender=DoctorAppointmentFile)
def delete_file_on__doctor_appointment_file_delete(sender, instance, **kwargs):
    print(1)
    if instance.file:
        print(2)
        instance.file.delete(save=False)