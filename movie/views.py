from django.shortcuts import render, redirect, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.db import IntegrityError
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import User, Movie, Watchlist, Recommendation
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


# Search For a Movie
def search_movie(request):
    if request.method == "GET":
        query = request.GET.get('q')  
        movies = None
        if query:
            # Perform a case-insensitive search on the original_title field
            movies = Movie.objects.filter(original_title__icontains=query)
        return render(request, 'movie/movie_list.html', {'movies': movies, 'query': query})


# Get Details of a particular movie
def movie_details(request, imdb_id):
    try:
        movie = Movie.objects.get(imdb_id=imdb_id)
    except Movie.DoesNotExist:
        return JsonResponse({'error': 'Movie not found'}, status=404)
    movie_details = {
        'id': movie.imdb_id,
        'poster': movie.poster_path,
        'title': movie.original_title,
        'genres': movie.genres,
        'ratings': movie.vote_average,
        'language': movie.original_language,
        'release_date': movie.release_date,
        'overview': movie.overview,
    }
    return JsonResponse(movie_details)


# Add and remove Movie to Watchlist
@login_required
def toggle_watchlist(request, imdb_id):
    movie = Movie.objects.get(imdb_id=imdb_id)
    watchlist_item, created = Watchlist.objects.get_or_create(user=request.user, movie=movie)
    if created:
        watchlist_item.watched = True
        watchlist_item.save()
        status = 'added'
    else:
        watchlist_item.delete()
        status = 'removed'
    return JsonResponse({'status': status})


#  Get Users Watchlist 
@login_required
def watchlist(request):
    watchlist_movies = Watchlist.objects.filter(user=request.user)
    return render(request, 'movie/watchlist.html', {'watchlist_movies': watchlist_movies})


# Remove a Movie from the Users watchlist
@csrf_exempt
@require_POST
def delete_movie(request, imdb_id):
    movie = Watchlist.objects.get(user=request.user, movie__imdb_id=imdb_id)
    movie.delete()
    return JsonResponse({'status': 'ok'})


# movie recommendations list 
def movie_recommendation_view(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            user = request.user
            # Generate movie recommendations for the current user
            context = generate_movies_context(user)
            return render(request, 'movie/movie_list.html', context)
        else:
            return redirect('register') 

    

# Generate recommendations when button is clicked
def generate_recommendations(request):
    if request.method == "POST":
        # Retrieve the user id from the request
        user_id = request.POST.get('user_id')
        user = User.objects.get(id=user_id)

        # Check if the user's watchlist is empty
        if not Watchlist.objects.filter(user=user).exists():
            # If the watchlist is empty, delete all old recommendations for this user
            Recommendation.objects.filter(user=user).delete()
        else:
            # If the watchlist is not empty, generate recommendations
            generate_movie_recommendations(int(user_id))

        return redirect('recommendations')
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=400)


# Recommendation Function according to users watchlist
def generate_movies_context(user):
    context = {}
    watched_movies = Watchlist.objects.filter(user=user, watched=True).values_list('movie_id', flat=True)
    recommended_movies = Recommendation.objects.filter(user=user, recommended=True).values_list('movie_id', flat=True)
    
    if not watched_movies and not recommended_movies:
        # Show top 30 popular movies for new users
        movies = Movie.objects.order_by('-vote_count')[:30]
    elif not recommended_movies:
        # Show top 30 popular unwatched movies
        movies = Movie.objects.exclude(id__in=watched_movies).order_by('-vote_count')[:30]
    else:
        # Show top 30 recommended movies
        movies = Movie.objects.filter(id__in=recommended_movies).order_by('-vote_count')[:30]
    
    context['movie_list'] = movies
    return context


def login_view(request):
    if request.user.is_authenticated:
        return redirect('recommendations')
    
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("recommendations"))
        else:
            return render(request, "movie/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "movie/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("login"))


def register(request):
    if request.user.is_authenticated:
        return redirect('recommendations')
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "movie/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "movie/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("recommendations"))
    else:
        return render(request, "movie/register.html")
    

# Function to generate movie recommendations for a user
def generate_movie_recommendations(user_id: int):
    THRESHOLD = 0.8
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        print(f"User with id {user_id} does not exist")
        return
    
    watched_movies_ids = Watchlist.objects.filter(user=user, watched=True).values_list('movie_id', flat=True)
    watched_movies = Movie.objects.filter(id__in=watched_movies_ids)
    
    # Get a limited number of popular unwatched movies based on vote count
    unwatched_movies = Movie.objects.exclude(id__in=watched_movies_ids).order_by('-vote_count')
    
    recommendations = []
    for unwatched_movie in unwatched_movies:
        will_recommend = False
        
        # Check similarity with each watched movie
        for watched_movie in watched_movies:
            try:
                similarity = similarity_between_movies(unwatched_movie, watched_movie)
            except Exception as e:
                print(f"Error calculating similarity: {e}")
                continue
            
            # If similarity exceeds threshold, recommend the movie
            if similarity >= THRESHOLD:
                will_recommend = True
                break
        
        # If recommended, update recommendation status
        if will_recommend:
            print(f"Find a movie recommendation for {user}: {unwatched_movie.original_title}")
            recommendations.append(unwatched_movie.original_title)
            Recommendation.objects.update_or_create(user=user, movie=unwatched_movie, defaults={'recommended': True})
        # Update or create recommendation status in database for unwatched movies that are not recommended
        else:
            Recommendation.objects.update_or_create(user=user, movie=unwatched_movie, defaults={'recommended': False})
    
    return recommendations



def check_valid_genres(genres: str) -> bool:
    if bool(genres and not genres.isspace()) and genres != 'na':
        return True
    else:
        return False


# Method to calculate Jaccard Similarity
def jaccard_similarity(list1: list, list2: list) -> float:
    s1 = set(list1)
    s2 = set(list2)
    return float(len(s1.intersection(s2)) / len(s1.union(s2)))


# Calculate the similarity between two movies
def similarity_between_movies(movie1: Movie, movie2: Movie) -> float:
    if check_valid_genres(movie1.genres) and check_valid_genres(movie2.genres):
        m1_generes = movie1.genres.split()
        m2_generes = movie2.genres.split()
        return jaccard_similarity(m1_generes, m2_generes)
    else:
        return 0
    
