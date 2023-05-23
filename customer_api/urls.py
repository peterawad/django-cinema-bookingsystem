from django.urls import path
from . import views

app_name = "cinema"

from .views import home, showinglist, FilmDetails, PurchaseTicket, CostOfTicket
from . import views
urlpatterns = [
     # Home page
    path("", views.home, name="home"),

    # Showing list page for a specific date
    path('showings/', showinglist, name='showinglist'),

    # Showing detail page for a specific showing
    path("showing/<int:pk>/", views.Showing, name="showing_detail"),

    # Purchase ticket page for a specific showing and ticket type
    path("showing/<int:showing_pk>/purchase/<slug:ticket_type>/", views.PurchaseTicket.as_view(), name="purchase_ticket"),

    # Confirmation page for a ticket purchase
    #path("showing/<int:showing_pk>/purchase/<slug:ticket_type>/confirm/", views.Purchase TicketConfirm .as_view(), name="purchase_ticket_confirm"),
]




"""
urlpatterns = [
    
    # Home page
    path("", views.home, name="home"),
    # Showing list page for a specific date
    #path("showing_list?<str:date>/", views.showing_list.as_view(), name="showing_list"),
    path("/showing_list.html", views.showing_list.as_view(), name="showing_list"),
    # Showing detail page for a specific showing
    path("showing_detail/<int:pk>/", views.FilmDetails.as_view(), name="film_details"),
    # Purchase ticket page for a specific showing and ticket type
    path("purchase_ticket/<int:showing_pk>/<slug:ticket_type>/", views.PurchaseTicket.as_view(), name="purchase_ticket"),
    # Confirmation page for a ticket purchase
    #path("purchase_confirm/<int:showing_pk>/<slug:ticket_type>/", views.PurchaseConfirm.as_view(), name="purchase_confirm"),
]
"""