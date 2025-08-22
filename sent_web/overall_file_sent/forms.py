
from django import forms
from .models import OverallSentiment
import re



class OverallSentimentForm(forms.ModelForm):
    class Meta:
        model = OverallSentiment
        fields = ('name_id','input_file','is_public')
    
    def __init__(self,*args,**kargs):
        super().__init__(*args,**kargs)

        self.fields['name_id'].label = '<label class="form-label">Name</label>'
        self.fields['name_id'].widget.attrs.update(
            {'class':'form-control','placeholder':'Name...'}
        )

        self.fields['is_public'].label = '<label class="form-check-label">Is public</label>' #{{form.is_public.label|safe}}
        self.fields['is_public'].widget.attrs.update(
            {'class':'form-check-input'}
        )

    @staticmethod
    def is_name_id_valid(x):
        match_ = re.match('[\w\d\' ]{3,}',x)
        return match_.group(0) == x if match_ else False
    
    def clean_name_id(self):
        cleaned_data = self.cleaned_data.get('name_id')
        invalid_characters = re.findall('[^\w ]',cleaned_data)
        if len(invalid_characters) > 0:
            raise forms.ValidationError(f"Invalid characters: {invalid_characters}")
        elif not OverallSentimentForm.is_name_id_valid(cleaned_data):
            raise forms.ValidationError(f"Invalid name")
        return cleaned_data