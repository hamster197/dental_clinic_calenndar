import csv

from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import path

from apps.guides.forms import PriceQuideForm
from apps.guides.models import *

# Register your models here.
admin.site.register(DoctorSpecialization)

@admin.register(PriceImport)
class PriceImportModelAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'date_added', 'csv_file',]
    readonly_fields = ['user_id', 'csv_file',]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(PraisCategory)
class PraisCategoryModelAdmin(admin.ModelAdmin):
    search_fields = ['title', ]
    search_help_text = 'Название'

@admin.register(PraisSubCategory)
class PraisSubCategoryModelAdmin(admin.ModelAdmin):
    list_display = [ 'title', 'categoty_id']
    list_filter = ['categoty_id__title',  ]
    search_fields = ['title',  'categoty_id']
    search_help_text = 'Название и категрия'

@admin.register(PriceQuide)
class PriceQuideModelAdmin(admin.ModelAdmin):
    list_display = [ 'code', 'title', 'subcategoty_id', 'price_base', 'duration',]
    list_filter = ['subcategoty_id',  ]
    search_fields = ['code', 'title', ]
    search_help_text = 'Название и код'


    def get_urls(self):
        urls = super().get_urls()
        urls.insert(-1, path('csv-upload/', self.upload_csv))

        return urls

    def upload_csv(self, request):
        category_count = subcategory_count = prais_new = praise_updated  = 0
        if request.method == 'POST':

            form = PriceQuideForm(request.POST, request.FILES)
            if form.is_valid():
                form_object = form.save(commit=False)
                form_object.save(user_id=request.user)

                with (form_object.csv_file.open('r') as csv_file):
                    rows = csv.DictReader(csv_file, delimiter=',')
                    fields_flag = True
                    if not 'code' in rows.fieldnames:
                        fields_flag = False
                    elif not 'title' in rows.fieldnames:
                        fields_flag = False
                    elif not 'category' in rows.fieldnames:
                        fields_flag = False
                    elif not 'subcategory' in rows.fieldnames:
                        fields_flag = False
                    elif not 'base' in rows.fieldnames:
                        fields_flag = False
                    elif not 'Group_a' in rows.fieldnames:
                        fields_flag = False
                    elif not 'Group_b' in rows.fieldnames:
                        fields_flag = False
                    elif not 'Group_ls' in rows.fieldnames:
                        fields_flag = False
                    elif not 'Croup_Ch_B' in rows.fieldnames:
                        fields_flag = False

                    if not fields_flag:
                        messages.warning(request, 'Неверные заголовки у файла')
                        return HttpResponseRedirect(request.path_info)

                    for row in rows:
                        base = group_a = group_b = group_ls = group_ch_b = 0
                        category, created = PraisCategory.objects.get_or_create(title=row['category'])
                        if created:
                            category_count += 1
                        subcategory, created = PraisSubCategory.objects.get_or_create(categoty_id=category, title=row['subcategory'])
                        if created:
                            subcategory_count += 1
                        if row['base']:
                            base = row['base'].replace("₽", "").replace(".", "").split(',')[0]
                        if row['Group_a']:
                            group_a = row['Group_a'].replace("₽", "").replace(".", "").split(',')[0]
                        if row['Group_b']:
                            group_b = row['Group_b'].replace("₽", "").replace(".", "").split(',')[0]
                        if row['Group_ls']:
                            group_ls = row['Group_ls'].replace("₽", "").replace(".", "").split(',')[0]
                        if row['Croup_Ch_B']:
                            group_ch_b = row['Croup_Ch_B'].replace("₽", "").replace(".", "").split(',')[0]

                        values_for_update = {"title":row['title'], "subcategoty_id": subcategory, 'price_base':base,
                                             'price_croup_a':group_a, 'price_croup_b':group_b, 'price_croup_ls':group_ls,
                                             'price_croup_ch_b':group_ch_b,}
                        price, created = PriceQuide.objects.update_or_create(code=row["code"], defaults=values_for_update)
                        if created:
                            prais_new += 1
                        else:
                            praise_updated += 1

        form = PriceQuideForm()
        return render(request, 'admin/csv_import_page.html',
                      {'form': form, #'category_count':category_count, 'subcategory_count':subcategory_count,
                       'prais_new':prais_new, 'praise_updated':praise_updated})

@admin.register(MKB10Classes)
class MKB10ClassesModelAdmin(admin.ModelAdmin):
    search_fields = ['title',  ]
    search_help_text = 'Название'

@admin.register(MKB10Quide)
class MKB10QuideModelAdmin(admin.ModelAdmin):
    list_display = ['class_id', 'code', 'title', ]
    list_filter = ['class_id__title', 'code', ]
    search_fields = ['title',  ]
    search_help_text = 'Название'

@admin.register(DentalFormula)
class MKB10QuideModelAdmin(admin.ModelAdmin):
    list_display = ['tooth_number', 'position_vertical', 'position_horizontal', 'image', ]
    list_filter = ['tooth_number', 'position_vertical', ]
