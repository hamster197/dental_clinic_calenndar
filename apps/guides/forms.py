from django.forms import ModelForm
from .models import PriceImport

class PriceQuideForm(ModelForm):
    class Meta:
        model = PriceImport
        fields = ('csv_file',)

