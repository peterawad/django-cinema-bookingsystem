from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView, GenericAPIView
from rest_framework.response import Response
from .models import Showing, Ticket, Film
from .serializer import ShowingSerializer, TicketSerializer, FilmSerializer
from datetime import datetime
from django.shortcuts import render

def home(request):
    return render(request, "movie/home.html")

def showinglist(request):
    if request.method == 'POST':
        selected_date = request.POST.get('date')
        
        if selected_date:
            try:
                date = datetime.strptime(selected_date, '%Y-%m-%d').date()
                showings = Showing.objects.filter(start_time__date=date)
                return render(request, 'movie/showinglist.html', {'showings': showings})
            except ValueError:
                pass
    return render(request, "movie/home.html")

class FilmDetails(RetrieveAPIView):
    queryset = Film.objects.all()
    serializer_class = FilmSerializer

class PurchaseTicket(CreateAPIView):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

class CostOfTicket(GenericAPIView):
    def get(self, request, *args, **kwargs):
        ticket = Ticket(showing_id=kwargs['showing_id'], ticket_type=kwargs['ticket_type'], quantity=kwargs['quantity'])
        cost = ticket.get_cost()
        return Response({'cost': cost})


import psycopg2
def connection_showing(Show_date):   
    try:    
        connection = psycopg2. connect (user="postgres",
        password="1998", host="localhost", port="5432", database="movie")
        cursor = connection.cursor ()
        postgreSQL_select_Query = "SELECT * fROM public.showing WHERE film_date='",Show_date
        cursor. execute (postgreSQL_select_Query)
        list = cursor. fetchall ()
        return list
    except (Exception, psycopg2.Error) as error:
        print ("Error while fetching data from PosteresoL", error)
    finally:
        if connection:
            cursor.close() 
            connection.close()
            print ("PostgreSQL connection is closed")
