from django import forms
from django.core.exceptions import ValidationError
from .models import Quiz, Question, Flashcard, StudySession
from notes.models import Note, Category

class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'source_note']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter quiz title...'}),
            'source_note': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['source_note'].queryset = Note.objects.filter(user=self.user)
            self.fields['source_note'].empty_label = "Select Note (Optional)"


class QuestionForm(forms.Form):
    question_text = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'What is the question?'}),
        label="Question Text"
    )
    option_a = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option A'}))
    option_b = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option B'}))
    option_c = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option C'}))
    option_d = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option D'}))
    
    CORRECT_CHOICES = [
        ('A', 'Option A'),
        ('B', 'Option B'),
        ('C', 'Option C'),
        ('D', 'Option D'),
    ]
    correct_option = forms.ChoiceField(choices=CORRECT_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    explanation = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Why is this correct?'}),
        label="Explanation"
    )


class FlashcardForm(forms.ModelForm):
    class Meta:
        model = Flashcard
        fields = ['front', 'back', 'source_note']
        widgets = {
            'front': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Front of the card (e.g. Question/Term)'}),
            'back': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Back of the card (e.g. Answer/Definition)'}),
            'source_note': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['source_note'].queryset = Note.objects.filter(user=self.user)
            self.fields['source_note'].empty_label = "Select Note (Optional)"


class StartSessionForm(forms.ModelForm):
    class Meta:
        model = StudySession
        fields = ['subject', 'category', 'notes']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'What are you studying today? (e.g. Python OOP)'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Session notes / goals...'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['category'].queryset = Category.objects.filter(user=self.user)
            self.fields['category'].empty_label = "Select Subject Category (Optional)"
