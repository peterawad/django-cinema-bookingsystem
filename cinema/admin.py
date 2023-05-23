from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.contrib.auth import get_permission_codename
from django.db.models import Sum
from djmoney.models.fields import Money
from django.http import HttpResponseForbidden
from django.utils import timezone
from django import forms
from django.core.exceptions import PermissionDenied


# Registering all models here.

from .models import User, Theater, Screen, Category, Movie, Ticket

class MainUserAdmin(UserAdmin):
    readonly_fields = ['groups']
    additional_fields = ['club_name','email', 'role', 'date_of_birth', 'phone', 'land_phone', 'city', 'address', 'postal_code', 'balance']

    def get_fieldsets(self, request, obj):
        if obj is None:
            idx = 0 # add form
        else:
            idx = 1 # edit form

        fieldsets = super(MainUserAdmin, self).get_fieldsets(request, obj)
        for field in self.additional_fields:
          if field not in fieldsets[idx][1]['fields']:
              fieldsets[idx][1]['fields'] += (field, )

        return fieldsets

    def save_related(self, request, form, formsets, change, **kwargs):
        super(MainUserAdmin, self).save_related(request, form, formsets, change)
        user = User.objects.get(username=form.cleaned_data['username'])
        if user.role is None:
            user.groups.clear()
        else:
            group = Group.objects.filter(name=User.GROUPS[user.role])
            user.groups.set(group)


class ScreenAdmin(admin.ModelAdmin):
    readonly_fields = ["is_occupied"]

    def save_model(self, request, obj, form, change):
        if obj.movie is not None:
            now = timezone.now()  
            if now >= obj.movie.starts_at and now <= obj.movie.ends_at:
                obj.is_occupied = True
            else:
                obj.is_occupied = False
        else:
            Ticket.objects.all().filter(screen=obj.id).delete()
            obj.is_occupied = False

        super().save_model(request, obj, form, change)

        if obj.movie is not None:
            ticker_count = Ticket.objects.all().filter(screen=obj.id).count()
            if ticker_count == 0:
                if obj.type == Screen.Child:
                    price = 5
                elif obj.type == Screen.Student:
                    price = 10
                elif obj.type == Screen.Adult:
                    price = 15
                else:
                    price = 10
                tickets = []
                for i in range(1, obj.total_seats + 1):
                    tickets.append(Ticket(screen=obj, seat_number=i, price=price))
                Ticket.objects.bulk_create(tickets)


class MovieForm(forms.ModelForm):
    description = forms.CharField(widget=forms.Textarea())


class MovieAdmin(admin.ModelAdmin):
    readonly_fields = ["is_active", "created_by"]
    form = MovieForm

    def save_model(self, request, obj, form, change):
        if timezone.now() > obj.ends_at:
            obj.is_active = False
        else:
            obj.is_active = True

        obj.created_by = request.user
        super().save_model(request, obj, form, change)

class TicketAdmin(admin.ModelAdmin):
    readonly_fields = ["price", "issued_at"]

    def save_model(self, request, obj, form, change):
        if obj.screen.type == Screen.Adult:
            obj.price = 15
        elif obj.screen.type == Screen.Student:
            obj.price = 10
        elif obj.screen.type == Screen.Child:
            obj.price = 5
        else:
            obj.price = 15

        if obj.customer is None:
            obj.issued_at = None
        else:
            if obj.issued_at is None:
                obj.issued_at = timezone.now()

        super().save_model(request, obj, form, change)

    @admin.action(
        description='Buy selected ticket',
        permissions=['buy_ticket']
    )
    def buy_ticket(modeladmin, request, queryset):
        user = request.user
        sum = queryset.aggregate(Sum('price'))
        msg_change_tickets = 'Ticket/s are no longer availible, please change the ticket/s.'
        if not queryset:
            return HttpResponseForbidden(msg_change_tickets)

        sum = Money(sum['price__sum'], queryset[0].price.currency.code)
        percentage = 0
        # if user.role == user.STUDENT:
        #     percentage = 10
        # elif user.role == user.Child:
        #     percentage = 20
        if user.role == User.CLUB_MANAGER:
            percentage = 30

        sum_discounted = sum - sum * percentage / 100
        if sum_discounted > user.balance:
            msg = 'Error: account balance is too low. %s < %s' %(user.balance, sum)
            if percentage != 0:
                msg = 'Error: account balance is too low. %s < %s(price discounted by %s%% from %s)' %(user.balance, sum_discounted, percentage, sum)
            return HttpResponseForbidden(msg)
        for ticket in queryset:
            if ticket.customer is not None:
                 return HttpResponseForbidden(msg_change_tickets)
        for ticket in queryset:
            ticket.customer = user
            ticket.save()

        user.balance = user.balance - sum_discounted
        user.save()

    def has_buy_ticket_permission(self, request):
        opts = self.opts
        codename = get_permission_codename('buy', opts)
        return request.user.has_perm('%s.%s' % (opts.app_label, codename))

    actions = [buy_ticket]

    def get_queryset(self, request):
        user = request.user
        if user.is_superuser == False and self.has_buy_ticket_permission(request):
            return Ticket.objects.filter(customer__isnull=True) | Ticket.objects.filter(customer=user.id)

        return super().get_queryset(request)

admin.site.register(User, MainUserAdmin)
admin.site.register(Theater)
admin.site.register(Screen, ScreenAdmin)
admin.site.register(Movie, MovieAdmin)
admin.site.register(Category)
admin.site.register(Ticket, TicketAdmin)
