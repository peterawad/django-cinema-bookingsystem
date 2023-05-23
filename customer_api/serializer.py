from rest_framework import serializers
from .models import Showing, Ticket, Film

class ShowingSerializer(serializers.ModelSerializer):
    film_title = serializers.CharField(source='film.title', read_only=True)
    class Meta:
        model = Showing
        fields = ['id', 'film_title', 'start_time', 'end_time']

class FilmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Film
        fields = ['title', 'age_rating', 'duration', 'trailer']

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['showing', 'customer', 'ticket_type', 'quantity']
