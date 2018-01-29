from django.forms import ModelForm
from main.models import Opus, Progress


class OpusForm(ModelForm):
    class Meta:
        model = Opus
        fields = ['name', 'comment', 'total']


class ProgressForm(ModelForm):
    class Meta:
        model = Progress
        fields = ['current', 'weblink']
