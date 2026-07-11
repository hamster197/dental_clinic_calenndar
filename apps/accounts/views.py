from django.shortcuts import render
from django.views.generic import TemplateView

from config.mixins import DoctorExistsMixin
from config.settings import DOCTOR_BREADCRUMBS_URL


# Create your views here.
class MainView(DoctorExistsMixin, TemplateView):
    template_name = 'accounts/main.html'

    def get_breadcrumbs(self):
        crumbs = []
        crumbs.append({'title': 'Главаная(каледарь)',  'url': DOCTOR_BREADCRUMBS_URL})

        return crumbs

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = self.get_breadcrumbs()
        print(1, self.get_breadcrumbs())
        return context