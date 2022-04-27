from django import forms
from django.forms import ModelForm
from .models import *


class DateInput(forms.DateInput):
    input_type = 'date'

class EventForm(forms.ModelForm):
    title=forms.CharField(widget=forms.TextInput(attrs={'placeholder':' Add new Event...'}))
    class Meta:
        model=Event
        exclude = ['paid', 'published', 'created_by']
        widgets = {
            'start_date': DateInput(),
            'end_date': DateInput(),
        }