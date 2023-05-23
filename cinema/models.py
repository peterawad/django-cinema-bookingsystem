from django.db import models
from django.contrib.auth.models import User, AbstractUser, Group
from django.core.validators import MinValueValidator, MaxValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from djmoney.models.fields import MoneyField
from django.core.exceptions import ValidationError
from django_countries.fields import CountryField
from decimal import Decimal
from djmoney.models.validators import MinMoneyValidator
from datetime import date
from pprint import pprint

# Create models

class User(AbstractUser):
    CINEMA_MANAGER = 'CINEMA_MANAGER'
    CLUB_MANAGER = 'CLUB_MANAGER'
    STUDENT = 'STUDENT'
    CUSTOMER = 'CUSTOMER'
    Adult= 'Adult'
    Child= 'Child'

    GROUPS = {
        CINEMA_MANAGER: 'Cinema Manager',
        CLUB_MANAGER: 'Club Manager',
        STUDENT: 'Student',
        CUSTOMER: 'Customer',
        Adult: 'Adult',
        Child: 'Child',
    }

    # CHOICES_ROLE = (
    #     (CINEMA_MANAGER, 'Cinema Manager'),
    #     (CLUB_MANAGER, 'Club Manager'),
    #     (STUDENT, 'Student'),
    #     (CUSTOMER, 'Customer'),
    # )
    CHOICES_ROLE = (
        (CINEMA_MANAGER, 'Cinema Manager'),
        (CLUB_MANAGER, 'Club Manager'),
        (STUDENT, 'Student'),
        (Adult, 'Adult'),
        (Child, 'Child'),
    )

    club_name = models.CharField(max_length=25, null=True, blank=True)
    email = models.EmailField(null=False, blank=False, unique=True)
    role = models.CharField(max_length=20, choices=CHOICES_ROLE, null=True, blank=True)
    date_of_birth = models.DateField(max_length=50, null=True, blank=True, validators=[MaxValueValidator(date.today())])
    phone = PhoneNumberField(null=True, blank=True, unique=True)
    land_phone = PhoneNumberField(null=True, blank=True, unique=True)
    country = CountryField(max_length=2, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    postal_code = models.CharField(max_length=50, null=True, blank=True)
    balance = MoneyField(decimal_places=2, null=False, blank=False, default=Decimal(0), default_currency='GBP', max_digits=11, validators=[MinMoneyValidator(Decimal(0))])

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.role == self.CLUB_MANAGER:
            if self.club_name is None:
                 raise ValidationError('Club name is required for a club manager.')
            if self.date_of_birth is None:
                 raise ValidationError('Date of birth is required for a club manager.')
            if self.phone is None:
                 raise ValidationError('Phone is required for a club manager.')
            if self.country is None:
                 raise ValidationError('Country is required for a club manager.')
            if self.city is None:
                 raise ValidationError('City of birth is required for a club manager.')
            if self.address is None:
                 raise ValidationError('Address is required for a club manager.')
            if self.postal_code is None:
                 raise ValidationError('Postal code is required for a club manager.')
        
        if self.balance is not None and self.balance.currency.code != 'GBP':
            raise ValidationError('British pound isclub_name = models.CharField(max_length=50, null=True, blank=True) only allowed currency for a balance.')

class Theater(models.Model):
    name = models.CharField(max_length=200, unique=True)
    location = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True, verbose_name='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_screens(self, is_authenticated):
        if is_authenticated:
            return Screen.objects.filter(theater=self.id).order_by('name')
        else:
            return Screen.objects.filter(theater=self.id, is_active=True).order_by('name')

    def get_movies(self, is_authenticated):
        if is_authenticated:
            return Movie.objects.filter(screen__theater=self.id).order_by('starts_at')
        else:
            return Movie.objects.filter(screen__theater=self.id, screen__is_active=True, is_active=True).order_by('starts_at')

class Category(models.Model):
    class Meta:
        verbose_name_plural = "categories"

    name = models.CharField(max_length=200, unique=True)
    is_active = models.BooleanField(default=True, verbose_name='active')

    def __str__(self):
        return self.name

class Movie(models.Model):
    CHOICES_AGE_RATING = (
        ('G', 'G'),
        ('PG', 'PG'),
        ('PG-13', 'PG-13'),
        ('R', 'R'),
        ('NC-17', 'NC-17'),
        ('18+', '18+'),
    )

    category = models.ForeignKey(Category, on_delete=models.RESTRICT)
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=500, null=False, blank=False)
    image = models.ImageField(upload_to='cinema/static/storage/', null=True, blank=True, editable=True)
    duration = models.DurationField(null=False, blank=False)
    release_date = models.DateField(max_length=500, null=False, blank=False)
    age_rating = models.CharField(max_length=5, null=False, blank=False, choices=CHOICES_AGE_RATING)
    starts_at = models.DateTimeField('start date', null=False, blank=False)
    ends_at = models.DateTimeField('end date', null=False, blank=False)
    is_active = models.BooleanField(editable=False, verbose_name='active')
    created_by = models.ForeignKey(User, on_delete=models.RESTRICT, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def clean(self):
        if self.starts_at is not None and self.starts_at > self.ends_at:
            raise ValidationError('Start date is after end date.')
        if hasattr(self, 'category') and self.category.is_active == False:
            raise ValidationError('The category is not active.')

    def get_screens(self):
        return Screen.objects.filter(movie=self.id, is_active=True, theater__is_active=True).order_by('name')

class Screen(models.Model):
    class Meta:
        unique_together = ('theater', 'name')

    Student = 'Student'
    Adult = 'Adult'
    Child= 'Child'

    CHOICES_TYPE = (
        (Student, 'Student'),
        (Adult, 'Adult'),
        (Child, Child),
    )

    theater = models.ForeignKey(Theater, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=CHOICES_TYPE)
    total_seats = models.PositiveIntegerField(default=10, validators=[MinValueValidator(10), MaxValueValidator(100)])
    is_active = models.BooleanField(default=True, verbose_name='active')
    is_occupied = models.BooleanField(editable=False, verbose_name='occupied')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        name = self.theater.name + ": " + self.name
        if self.movie is not None:
            name = name + ": " + self.movie.name
        return name

    def clean(self):
        if hasattr(self, 'theater') and self.theater is not None and self.theater.is_active == False:
            raise ValidationError('The theater is not active.')
        if hasattr(self, 'movie') and self.movie is not None and self.movie.is_active == False:
            raise ValidationError('The movie is not active.')

    def get_total_seats_available(self):
        return Ticket.objects.filter(screen=self.id, customer__isnull=True).count()

class Ticket(models.Model):
    class Meta:
        unique_together = ('screen', 'seat_number')
        permissions = [
            ("buy_ticket", "Can buy ticket"),
        ]

    id = models.AutoField(primary_key=True, verbose_name='number')
    screen = models.ForeignKey(Screen, on_delete=models.CASCADE)
    customer = models.ForeignKey(User, on_delete=models.RESTRICT, null=True, blank=True)
    seat_number = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    price = MoneyField(decimal_places=2, default_currency='GBP', max_digits=4, editable=False)
    issued_at = models.DateTimeField(editable=False, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        name = self.screen.theater.name + ": " + self.screen.name + ": seat number " + str(self.seat_number)
        if self.customer is not None:
            name = name + ": " + self.customer.username
        return name

    def clean(self):
        if hasattr(self, 'screen') and self.screen.theater.is_active == False:
            raise ValidationError('Can not issue a ticket for inactive theater.')
        if hasattr(self, 'screen') and self.screen.movie is None:
            raise ValidationError('Can not issue a ticket without adding a movie to the screen first.')
        if hasattr(self, 'screen') and self.screen.is_active == False:
            raise ValidationError('Can not issue a ticket for inactive screen.')
        if hasattr(self, 'screen') and self.seat_number is not None and self.seat_number > self.screen.total_seats:
            raise ValidationError('The seat number "' + str(self.seat_number) + '" is higher than the total nubber of seats "' + str(self.screen.total_seats) + '".')
        if hasattr(self, 'customer') and self.customer is not None and self.customer.is_active == False:
            raise ValidationError('The customer is not active.')

Group.add_to_class('is_active', models.BooleanField(default=True, verbose_name='active'))
