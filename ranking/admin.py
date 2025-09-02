from django.contrib import admin
from .models import RankingProject, SearchEngine, Keyword, RankingSnapshot

admin.site.register(RankingProject)
admin.site.register(SearchEngine)
admin.site.register(Keyword)
admin.site.register(RankingSnapshot)
