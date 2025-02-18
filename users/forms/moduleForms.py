from django import forms

class ExerciseAnswerForm(forms.Form):
    
    def __init__(self, *args, **kwargs):
        exercise = kwargs.pop('exercise')  # Get exercise object
        super().__init__(*args, **kwargs)
        for question in exercise.questions.all():
            self.fields[f'answer_{question.id}'] = forms.CharField(
                label=question.question_text, 
                widget=forms.TextInput(attrs={'placeholder': 'Your answer here'})
            )
