from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Bookmarks, CustomUser


class BookmarkForm(forms.ModelForm):
    class Meta:
        model = Bookmarks
        fields = 'title', 'url', 'description', 'tags', 'is_public'





class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text='Required.')
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user






class BookmarkImportForm(forms.Form):
    html_file = forms.FileField(
        label='Upload HTML Bookmark File',
        help_text='Export bookmarks from your browser (Chrome, Firefox, Safari, etc.)',
        widget=forms.FileInput(attrs={
            'accept': '.html',
            'class': 'form-control'
        })
    )
    is_public = forms.BooleanField(
        label='Make imported bookmarks public?',
        required=False,
        initial=True,
        help_text='Check to make imported bookmarks visible to other users'
    )



