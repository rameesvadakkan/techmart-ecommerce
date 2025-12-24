from django import forms
from .models import ProductRating

class RatingForm(forms.ModelForm):
    class Meta:
        model = ProductRating
        fields = ['rating', 'review']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'review': forms.Textarea(attrs={'rows': 4}),
        }