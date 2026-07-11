from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.guides.models import DentalFormula
from apps.patients.models import DoctorAppointment, DentalFormulaAppointment


@receiver(post_save, sender=DoctorAppointment)
def instance_create(sender, instance,  created, **kwargs, ):
    if created:
        new_instances = []
        for obj in DentalFormula.objects.all():
            new_instances.append(DentalFormulaAppointment(appointment_id=instance , dental_formula_id=obj, ))

        DentalFormulaAppointment.objects.bulk_create(new_instances)


