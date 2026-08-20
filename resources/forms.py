from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from .models import Resource
from notes.models import Category

class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ['title', 'description', 'link', 'resource_type', 'category']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Resource Title...'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional brief description...'}),
            'link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com/learn-path'}),
            'resource_type': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['category'].queryset = Category.objects.filter(user=self.user)
            self.fields['category'].empty_label = "Select Category (Optional)"

    def clean_title(self):
        title = self.cleaned_data.get('title', '').strip()
        if not title:
            raise ValidationError("Title is required.")
        return title

    def clean_link(self):
        link = self.cleaned_data.get('link', '').strip()
        if not link:
            raise ValidationError("Resource URL link is required.")
        
        # URL validation
        validator = URLValidator()
        try:
            validator(link)
        except ValidationError:
            raise ValidationError("Enter a valid HTTP/HTTPS URL.")

        if not (link.startswith('http://') or link.startswith('https://')):
            raise ValidationError("URL must start with http:// or https://")

        return link

    def clean_category(self):
        category = self.cleaned_data.get('category')
        if category and self.user and category.user != self.user:
            raise ValidationError("Invalid category selected.")
        return category
