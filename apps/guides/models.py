from django.db import models

from django.contrib.auth import get_user_model

from apps.guides.constants import ToothChoises


# Create your models here.
class DoctorSpecialization(models.Model):
    title = models.CharField('Cпециализация', max_length=150, unique=True, blank=False)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Cпециализация доктора'
        verbose_name_plural = 'Cпециализация докторов'
        ordering = ['title',]


class MKB10Classes(models.Model):
    title = models.CharField('Класс', max_length=255, unique=True, blank=False, )

    class Meta:
        verbose_name = 'МКБ-10 (справочник классов)'
        verbose_name_plural = 'МКБ-10 (справочник классов)'

    def __str__(self):
        return self.title

class MKB10Quide(models.Model):
    class_id = models.ForeignKey(MKB10Classes, verbose_name='Класс', on_delete=models.CASCADE, related_name='mkb10_class_id',  )
    code = models.CharField('Код', max_length=10, unique=True, blank=False, )
    title = models.CharField('Название', max_length=255, blank=False, )

    class Meta:
        verbose_name = 'МКБ-10'
        verbose_name_plural = 'МКБ-10'
        # indexes = [
        #     models.Index(fields=['class_id', 'code', 'title'], name='mkb10_quide__idx'),
        # ]

    def __str__(self):
        return '%s, %s %s' % (self.code, self.class_id, self.title)
        # return '%s, %s' % (self.code, self.class_id, )

class PraisCategory(models.Model):
    title = models.CharField('Класс', max_length=255, unique=True, blank=False )

    class Meta:
        verbose_name = 'Прайс категория'
        verbose_name_plural = 'Прайс категории'

    def __str__(self):
        return self.title

class PraisSubCategory(models.Model):
    categoty_id = models.ForeignKey(PraisCategory, verbose_name='Категория', on_delete=models.CASCADE,
                                 related_name='price_sub_category_categoty_id')
    title = models.CharField('Подкатегория', max_length=255, )

    class Meta:
        verbose_name = 'Прайс подкатегория'
        verbose_name_plural = 'Прайс подкатегории'
        unique_together = ['categoty_id', 'title',]

    def __str__(self):
        return self.title

class PriceQuide(models.Model):
    code = models.CharField('Код', max_length=10, unique=True, blank=False )
    title = models.CharField('Название', max_length=255, )
    subcategoty_id = models.ForeignKey(PraisSubCategory, verbose_name='Подкатегория', on_delete=models.CASCADE,
                                       related_name='price_subcategoty_id')
    duration = models.PositiveIntegerField('Продолжительность выполнения услуги', default=20, )
    price_base = models.PositiveIntegerField('Цена базовая')
    price_croup_a = models.PositiveIntegerField('Цена группа А', )
    price_croup_b = models.PositiveIntegerField('Цена группа Б', )
    price_croup_ls = models.PositiveIntegerField('Цена группа ЛС', )
    price_croup_ch_b = models.PositiveIntegerField('Цена группа ЧБ', )

    class Meta:
        verbose_name = 'Прайс'
        verbose_name_plural = 'Прайс'
        unique_together = ['code', 'subcategoty_id']

    def __str__(self):
        return '%s, %s' % (self.code, self.title)


class PriceImport(models.Model):
    user_id = models.ForeignKey(get_user_model(), verbose_name='Пользователь',
                                   on_delete=models.CASCADE, related_name='price_import_user_id',)
    date_added = models.DateTimeField(auto_now_add=True)
    csv_file = models.FileField(upload_to='uploads/')

    class Meta:
        verbose_name = 'Прайс log'
        verbose_name_plural = 'Прайс log'

    def __str__(self):
        return str(self.date_added)

    def save(self, user_id=None, *args, **kwargs):
        if user_id:
            self.user_id=user_id

        super().save(*args, **kwargs)


class DentalFormula(models.Model):
    tooth_number = models.PositiveIntegerField('Номер', unique=True, )
    position_vertical = models.CharField(max_length=5, choices=ToothChoises.choices, )
    position_horizontal = models.PositiveIntegerField()
    image = models.ImageField(upload_to='tooth/',)
    checked_image = models.ImageField(upload_to='tooth/',)

    class Meta:
        verbose_name = 'Зубная формула(Справочнк)'
        verbose_name_plural = 'Зубная формула(Справочнк)'

    def __str__(self):
        return str(self.tooth_number)