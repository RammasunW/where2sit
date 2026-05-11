from django import forms
from .models import Room, ClassSchedule

INPUT = (
    "w-full px-3 py-2 border border-gray-300 "
    "rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
)

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = [
            'building',
            'number',
            'capacity',
        ]

        widgets = {
            'building': forms.Select(attrs={'class': INPUT}),
            'number': forms.TextInput(attrs={'class': INPUT}),
            'capacity': forms.NumberInput(attrs={'class': INPUT, 'min': 1}),
        }


class ClassScheduleForm(forms.ModelForm):
    class Meta:
        model = ClassSchedule
        fields = [
            'room',
            'course_name',
            'day_of_week',
            'start_time',
            'end_time',
        ]

        widgets = {
            'room': forms.Select(attrs={
                'class': INPUT
            }),

            'course_name': forms.TextInput(attrs={
                'class': INPUT,
                'placeholder': 'CSC 456 Lecture'
            }),

            'day_of_week': forms.Select(attrs={
                'class': INPUT
            }),

            'start_time': forms.TimeInput(attrs={
                'class': INPUT,
                'type': 'time'
            }),

            'end_time': forms.TimeInput(attrs={
                'class': INPUT,
                'type': 'time'
            }),
        }