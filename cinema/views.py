from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseNotFound
from pprint import pprint;

from .models import Theater, Movie

# Creating views here

def home(request):
    if request.user.is_authenticated:
        theaters = Theater.objects.order_by('created_at')
    else:
        theaters = Theater.objects.filter(is_active=True).order_by('created_at')

    for theater in theaters:
        theater.movies = theater.get_movies(request.user.is_authenticated)

    context = {'theaters': theaters}
    return render(request, 'cinema/home.html', context)

def movie(request, movie_id):
    try:
        movie = Movie.objects.get(id=movie_id)
    except ObjectDoesNotExist:
        return HttpResponseNotFound("404 page not found")

    movie.screens = movie.get_screens()
    for screen in movie.screens:
        screen.total_seats_available = screen.get_total_seats_available()

    context = {'movie': movie}
    return render(request, 'cinema/movie.html', context)
