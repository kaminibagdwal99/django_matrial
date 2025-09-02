from django.db import models

class RankingProject(models.Model):
    name = models.CharField(max_length=255)
    url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class SearchEngine(models.Model):
    ENGINE_CHOICES = [
        ("Google", "Google"),
        ("Google Mobile", "Google Mobile"),
        ("Bing", "Bing"),
        ("Yahoo", "Yahoo"),
    ]

    project = models.ForeignKey(RankingProject, on_delete=models.CASCADE, related_name='search_engines')
    name = models.CharField(max_length=100, choices=ENGINE_CHOICES)
    country = models.CharField(max_length=100)
    language = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.country})"

class Keyword(models.Model):
    project = models.ForeignKey(RankingProject, on_delete=models.CASCADE, related_name='keywords')
    keyword = models.CharField(max_length=255)

    def __str__(self):
        return self.keyword

class RankingSnapshot(models.Model):
    keyword = models.ForeignKey(Keyword, on_delete=models.CASCADE, related_name='snapshots')
    search_engine = models.ForeignKey(SearchEngine, on_delete=models.CASCADE, related_name='snapshots')  # ✅ NEW
    date = models.DateField()
    position = models.IntegerField()

    def __str__(self):
        return f"{self.keyword} - {self.search_engine} - {self.date}: {self.position}"
