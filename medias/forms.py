from django import forms
from .models import Article, Photo, Video


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['titre', 'accroche', 'contenu', 'image',
                  'categorie', 'date_publication', 'en_une', 'publie']
        widgets = {
            'titre':            forms.TextInput(attrs={'placeholder': 'Titre de l\'article'}),
            'accroche':         forms.TextInput(attrs={'placeholder': 'Accroche courte (300 cars max)'}),
            'contenu':          forms.Textarea(attrs={'rows': 12, 'placeholder': 'Contenu…'}),
            'date_publication': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.date_publication:
            self.fields['date_publication'].initial = self.instance.date_publication.strftime('%Y-%m-%dT%H:%M')


class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['image', 'legende', 'auteur', 'date', 'afficher']
        widgets = {
            'legende': forms.TextInput(attrs={'placeholder': 'Légende / description de la photo'}),
            'auteur':  forms.TextInput(attrs={'placeholder': 'Photographe (optionnel)'}),
            'date':    forms.DateInput(attrs={'type': 'date'}),
        }


class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['titre', 'description', 'thumbnail', 'url',
                  'type_video', 'date', 'afficher']
        widgets = {
            'titre':       forms.TextInput(attrs={'placeholder': 'Titre de la vidéo'}),
            'description': forms.TextInput(attrs={'placeholder': 'Description courte'}),
            'url':         forms.URLInput(attrs={'placeholder': 'https://youtube.com/watch?v=…'}),
            'date':        forms.DateInput(attrs={'type': 'date'}),
        }
