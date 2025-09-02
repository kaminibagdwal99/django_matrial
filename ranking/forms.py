from django import forms
from .models import RankingProject, SearchEngine, Keyword
from django.forms import modelformset_factory

class RankingProjectForm(forms.ModelForm):
    class Meta:
        model = RankingProject
        fields = ['name', 'url']

class SearchEngineForm(forms.ModelForm):
    class Meta:
        model = SearchEngine
        fields = ['name', 'country', 'language']

class KeywordForm(forms.ModelForm):
    class Meta:
        model = Keyword
        fields = ['keyword']

SearchEngineFormSet = modelformset_factory(SearchEngine, form=SearchEngineForm, extra=1, can_delete=True)
KeywordFormSet = modelformset_factory(Keyword, form=KeywordForm, extra=1, can_delete=True)
