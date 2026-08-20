from django import forms
from django.core.exceptions import ValidationError
from .models import Note, Category, Tag

class NoteForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.none(),
        widget=forms.CheckboxSelectMultiple(),
        required=False
    )

    class Meta:
        model = Note
        fields = ['title', 'content', 'category', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Note title...'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10, 'placeholder': 'Write your study notes here...'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['category'].queryset = Category.objects.filter(user=self.user)
            self.fields['category'].empty_label = "Select Category (Optional)"
            self.fields['tags'].queryset = Tag.objects.filter(user=self.user)

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if not title or not title.strip():
            raise ValidationError("Note title is required.")
        return title.strip()

    def clean_content(self):
        content = self.cleaned_data.get('content')
        if not content or not content.strip():
            raise ValidationError("Note content cannot be empty.")
        return content.strip()

    def clean_category(self):
        category = self.cleaned_data.get('category')
        if category and self.user and category.user != self.user:
            raise ValidationError("Invalid category selected.")
        return category

    def clean_tags(self):
        tags = self.cleaned_data.get('tags')
        if tags and self.user:
            for tag in tags:
                if tag.user != self.user:
                    raise ValidationError(f"Invalid tag selected: {tag.name}")
        return tags


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'color']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category Name (e.g. Mathematics)'}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not name:
            raise ValidationError("Category name is required.")
        if self.user:
            qs = Category.objects.filter(user=self.user, name__iexact=name)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError("You already have a category with this name.")
        return name


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tag Name (e.g. Exam, Important)'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not name:
            raise ValidationError("Tag name is required.")
        if self.user:
            qs = Tag.objects.filter(user=self.user, name__iexact=name)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError("You already have a tag with this name.")
        return name
