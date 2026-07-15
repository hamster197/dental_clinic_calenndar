import uuid
from django.contrib.auth import get_user_model
from django.db import models
from tinymce.models import HTMLField


from apps.guides.models import MKB10Quide, PriceQuide, DentalFormula


# Create your models here.
class DoctorAppointment(models.Model):
    date_created = models.DateField('Дата создания',auto_now_add=True)
    author_id = models.ForeignKey(get_user_model(), verbose_name='Создал',
                                on_delete=models.CASCADE, related_name='doctor_appointment_author_id',)
    patient_id = models.ForeignKey(get_user_model(), verbose_name='Пациент',
                                on_delete=models.CASCADE, related_name='doctor_appointment_patient_id',)
    text = HTMLField('Прочее ', blank=True)
    recomendations = HTMLField('Рекомендации ', blank=True)

    class Meta:
        verbose_name = 'Рекомендации и Прочее'
        verbose_name_plural = 'Приемы врача'
        ordering = ['-id']
        unique_together = ['patient_id', 'date_created']

    def __str__(self):
        return f'{self.date_created} {self.patient_id.last_name} {self.patient_id.first_name}'

class DoctorAppointmentFile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date_created = models.DateTimeField('Дата создания',auto_now_add=True)
    parent_id = models.ForeignKey(DoctorAppointment,
                                    on_delete=models.CASCADE, related_name='doctor_appointment_file_id',)

    file = models.FileField(verbose_name='фото', upload_to='%Y/%m/%d/',)


    class Meta:
        verbose_name = 'Прием пациента фото'
        verbose_name_plural = 'Прием пациента фото'

    @property
    def model_name(self):
        return self._meta.model_name

    def __str__(self):
        return str(self.file)


class AbstractDoctorAppointmentData(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author_id = models.ForeignKey(get_user_model(), verbose_name='Создал',
                                  on_delete=models.CASCADE, )
    appointment_id = models.ForeignKey(DoctorAppointment, verbose_name='Прием',
                                  on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s',)
    date_created = models.DateTimeField('Дата создания',auto_now_add=True)

    class Meta:
        abstract = True

    @property
    def model_name(self):
        return self._meta.model_name

class MKB10DoctorAppointmentData(AbstractDoctorAppointmentData):
    mkb10_id = models.ForeignKey(MKB10Quide, verbose_name='МКБ10',
                                  on_delete=models.CASCADE, related_name='doctor_appointment_mkb10_id', )

    class Meta:
        verbose_name = 'МКБ10'
        verbose_name_plural = 'Прием пациента МКБ10'
        unique_together = ['appointment_id', 'mkb10_id']

    def __str__(self):
        return str(self.mkb10_id)

class ServiceAppointmentData(AbstractDoctorAppointmentData):
    service_id = models.ForeignKey(PriceQuide, verbose_name='Услуга',
                                 on_delete=models.CASCADE, related_name='service_appointment_id', )
    doctor_id = models.ForeignKey(get_user_model(), verbose_name='Доктор',
                                  on_delete=models.CASCADE, related_name='service_doctor_appointment_id',)
    date_time = models.DateTimeField('Дата приема', )
    status = models.BooleanField('Услуга оказана?', default=False)

    class Meta:
        verbose_name = 'Услуга'
        verbose_name_plural = 'Прием пациента Услуги'
        ordering = ['date_time',]

class DentalFormulaAppointment(models.Model):
    appointment_id = models.ForeignKey(DoctorAppointment, verbose_name='Прием',
                                       on_delete=models.CASCADE, related_name='dental_formula_appointment_id',)
    dental_formula_id = models.ForeignKey(DentalFormula, verbose_name='Зубная формула',
                                   on_delete=models.CASCADE, related_name='dental_formula_appointment_id',)
    comment = HTMLField('Коментарий ', blank=True)
    author_id = models.ForeignKey(get_user_model(), verbose_name='Создал', null=True, blank=True,
                                  on_delete=models.CASCADE, related_name='dental_formula_author_id',)

    class Meta:
        verbose_name = 'Зубная формула'
        verbose_name_plural = 'Зубная формула'
        unique_together = ['appointment_id', 'dental_formula_id']
