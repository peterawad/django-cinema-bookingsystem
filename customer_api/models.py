from django.db import models
from django.contrib.auth.models import User

class Film(models.Model):
    title = models.CharField(max_length=100)
    age_rating = models.CharField(max_length=10)
    duration = models.IntegerField()
    trailer = models.TextField()

class Showing(models.Model):
    film = models.ForeignKey(Film, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

class Ticket(models.Model):
    showing = models.ForeignKey(Showing, on_delete=models.CASCADE)
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    TICKET_TYPES = (
        ('S', 'Student'),
        ('C', 'Child'),
        ('A', 'Adult'),
    )
    ticket_type = models.CharField(max_length=1, choices=TICKET_TYPES)
    quantity = models.IntegerField()

    def get_cost(self):
        if self.ticket_type == 'S':
            cost_per_ticket = 5.0
        elif self.ticket_type == 'C':
            cost_per_ticket = 7.0
        else:
            cost_per_ticket = 10.0
        return cost_per_ticket * self.quantity
