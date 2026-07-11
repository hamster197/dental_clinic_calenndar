from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.core.validators import MinLengthValidator

from django.contrib.auth import get_user_model
from .managers import UserManager



# Create your models here.
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField('email', unique=True, blank=False)

    first_name = models.CharField('Имя', max_length=30, blank=False, validators=[MinLengthValidator(2)],)
    last_name = models.CharField('Фамилия', max_length=30, blank=False)
    patronymic = models.CharField('Отчество', max_length=45, blank=True, validators=[MinLengthValidator(2)])
    phone = models.CharField('Телефон ', help_text='+7 *** *** ** **', max_length=12, blank=True)

    date_joined = models.DateTimeField('Дата регистрации', auto_now_add=True)
    last_login = models.DateTimeField('Последний вход', auto_now=True)
    is_active = models.BooleanField('Active', default=True)
    is_staff = models.BooleanField('Is_staff', default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-id']

    def __str__(self):
        return '%s %s %s' % (self.last_name, self.first_name, self.pacient_profile_user_id.date_birth)


class PacientProfile(models.Model):
    user_id = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='pacient_profile_user_id',)
    date_birth = models.DateField('Дата рождения', help_text='Только для пациентов')

    class Meta:
        verbose_name = 'Данные пациента'
        verbose_name_plural = 'Данные пациента'

    def __str__(self):
        return '%s %s %s' % (self.user_id.last_name, self.user_id.first_name, self.date_birth)

class DoctorProfile(models.Model):
    from ..guides.models import DoctorSpecialization
    user_id = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='doctor_profile_user_id',)
    doctor_specialization = models.ManyToManyField(DoctorSpecialization, verbose_name='Cпециализация доктора',
                                                   help_text='Только для врачей')

    class Meta:
        verbose_name = 'Данные врача'
        verbose_name_plural = 'Данные врача'
