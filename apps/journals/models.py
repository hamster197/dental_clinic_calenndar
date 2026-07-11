from django.contrib.auth import get_user_model
from django.db import models

from apps.patients.models import DoctorAppointment


# Create your models here.
class Mkb10ServiceJournal(models.Model):
    creation_date = models.DateTimeField('Дата создания', auto_now_add=True)
    type = models.CharField('Тип', max_length=25,)
    action = models.CharField('Действие', max_length=25,)
    author_id = models.ForeignKey(get_user_model(), verbose_name='Автор', on_delete=models.CASCADE,
                                  related_name='mkb10_service_journal_author_id', )
    appointment_id = models.ForeignKey(DoctorAppointment, verbose_name='Прием',
                                       on_delete=models.CASCADE,related_name='mkb10_service_journal_appointment_id', )
    title = models.CharField('Значение', max_length=25,)
    title_new = models.CharField('Новое значение', max_length=25,)

    class Meta:
        app_label = 'journals'
        verbose_name = 'Журнал редактирования приема мациентов МКБ10 и Услуги'
        verbose_name_plural = 'Журнал редактирования приема мациентов МКБ10 и Услуги'
        ordering = ['-creation_date']