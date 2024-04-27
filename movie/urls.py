from django.urls import path
from . import views

urlpatterns = [
    path('',views.movie_recommendation_view, name='recommendations'),
		path('search', views.search_movie, name='search_movie'),
		path('generate', views.generate_recommendations, name="generate"),
		path('watchlist', views.watchlist, name='watchlist'),
		path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
		
	# API path
	path('details/<str:imdb_id>/', views.movie_details, name='movie_details'),
	path('toggle_watchlist/<str:imdb_id>/', views.toggle_watchlist, name='toggle_watchlist'),
	path('delete/<str:imdb_id>/', views.delete_movie, name='delete'),
]