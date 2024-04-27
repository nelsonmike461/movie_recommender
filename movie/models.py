from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    pass


class Movie(models.Model):
    # IMDB id
    imdb_id = models.CharField(max_length=48, null=False)
    # Movie genres
    genres = models.CharField(max_length=200, null=True)
    # Original language
    original_language = models.CharField(max_length=20, null=True)
    # Original movie title
    original_title = models.CharField(max_length=500, null=False)
    # Movie release date
    release_date = models.IntegerField(default=1970)
    # Movie overview
    overview = models.TextField(max_length=2000, null=True)
    # Average voting for the movie
    vote_average = models.FloatField(default=0)
    # Total votes for ths movie
    vote_count = models.IntegerField(default=0)
    # The movie's poster path
    poster_path = models.CharField(max_length=64, null=True)
    # If this movie will be recommended
    recommended = models.ManyToManyField(User, through='Recommendation', related_name='recommended_movies')

    def __str__(self):
        return self.original_title
    

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    watched = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'movie')


class Recommendation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    recommended = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'movie')

    def __str__(self):
        return f'{self.movie} Recommended for {self.user}'
