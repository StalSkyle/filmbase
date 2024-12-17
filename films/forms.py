from dal import autocomplete
from django import forms

from .models import Country, Genre, Film, Person, NotificationSettings


class CountryForm(forms.ModelForm):
    class Meta:
        model = Country
        fields = ['name']


class GenreForm(forms.ModelForm):
    class Meta:
        model = Genre
        fields = ['name']


class FilmForm(forms.ModelForm):
    class Meta:
        model = Film
        fields = ['name', 'origin_name', 'slogan', 'length', 'year',
                  'trailer_url', 'cover', 'description', 'country', 'genres',
                  "director", 'people']
        widgets = {
            'people': autocomplete.ModelSelect2Multiple(
                url='films:person_autocomplete'),
            'director': autocomplete.ModelSelect2(
                url='films:person_autocomplete'),
            'country': autocomplete.ModelSelect2(
                url='films:country_autocomplete'),
        }


class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ['name', 'origin_name', 'birthday', 'photo']
        widgets = {
            "birthday": forms.DateInput(attrs={'type': 'date'},
                                        format="%Y-%m-%d")
        }


class EmailPostForm(forms.Form):
    name = forms.CharField(max_length=25)
    email = forms.EmailField()
    to = forms.EmailField()
    comments = forms.CharField(required=False, widget=forms.Textarea)


class NotificationSettingsForm(forms.ModelForm):
    class Meta:
        model = NotificationSettings
        fields = ['notification_types', 'notification_period']

    NOTIFICATION_TYPE_CHOICES = [
        ('add', 'Добавление нового фильма'),
        ('add_change', 'Добавление нового фильма или изменение имеющегося'),
        ('everything', 'Все изменения'),
    ]

    PERIOD_CHOICES = [
        ('daily', 'Раз в день'),
        ('weekly', 'Раз в неделю'),
        ('monthly', 'Раз в месяц'),
    ]

    notification_types = forms.MultipleChoiceField(
        choices=NOTIFICATION_TYPE_CHOICES,
        widget=forms.RadioSelect,
        label="Типы уведомлений"
    )

    notification_period = forms.ChoiceField(
        choices=PERIOD_CHOICES,
        widget=forms.RadioSelect,
        label="Периодичность получения уведомлений"
    )
