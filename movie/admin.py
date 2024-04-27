from django.contrib import admin

from .models import User, Movie, Watchlist, Recommendation
# Register your models here.

class UserAdmin(admin.ModelAdmin):
	list_display = ('id', 'username','email')
	ordering = ('id',)

class WatchlistAdmin(admin.ModelAdmin):
	list_display = ('user', 'movie', 'watched')

class RecommendationAdmin(admin.ModelAdmin):
	list_display = ('user', 'movie',)

admin.site.register(User, UserAdmin)
admin.site.register(Movie)
admin.site.register(Watchlist, WatchlistAdmin)
admin.site.register(Recommendation, RecommendationAdmin)