"""
Views in this module provide logic for templates that guide the booking process
"""

import json
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from .models import Trip
from .forms import DateChoiceForm


class SelectTripView(View):
    """
    Provides the user a set of choice options based on their search input in
    the products.TripsView
    """

    template_name = "bookings/trips_available.html"
    form_class = DateChoiceForm

    def get_searched_date(self):
        """ Deserialises the searched_date value from the session """

        searched_date = self.request.session['searched_date']
        searched_date = json.loads(searched_date)
        return searched_date

    def available_trips(self, destination, passengers):
        """ Find trips with enough seats for searched no. of passengers """

        available_trips = Trip.objects.filter(
            destination=destination
        ).filter(seats_available__gte=passengers)
        return available_trips

    def trips_matched_or_post_date(self, date):
        """
        Returns trips that either match or are post- searched_date
        Refine to trips with dates closest to searched_date
        limit to 3 results
        """

        available_trips = self.available_trips(
            self.request.session["destination_choice"],
            self.request.session["passenger_total"]
        )
        gte_dates = available_trips.filter(date__gte=date).order_by("date")[:3]
        return gte_dates

    def trips_preceding_date(self, date):
        """
        Returns trips that are pre- searched_date
        Refines to trips with dates closest to searched_date
        limits to 3 results
        """

        available_trips = self.available_trips(
            self.request.session["destination_choice"],
            self.request.session["passenger_total"]
        )
        lt_dates = available_trips.filter(date__lt=date).order_by("-date")[:3]
        return lt_dates

    def make_timezone_naive(self, obj):
        """ Turns date attribute to a time-zone naive date object """

        date_attr = obj.date
        date_string = date_attr.strftime("%Y-%m-%d")
        datetime_naive = datetime.strptime(date_string, "%Y-%m-%d")
        return datetime_naive

    def get_queryset(self):
        """ Creates as queryset that can be used in the ModelChoiceField of
        DateChoiceForm """

        searched_date = self.get_searched_date()
        gte_dates = self.trips_matched_or_post_date(searched_date)
        lt_dates = self.trips_preceding_date(searched_date)
        # Merge both queries
        trips = gte_dates | lt_dates
        return trips

    def post(self, request):
        """
        Takes the POST data from the DateChoiceForm and stores it in
        the session.
        """

        trips = self.get_queryset()
        form = self.form_class(request.POST, trips=trips)
        if form.is_valid():
            trip_choice = request.POST.get("trip")
            request.session["trip_choice"] = trip_choice
            return redirect('trip_confirmation')

    def get(self, request):
        """
        Initialises the DateChoiceForm with data from SearchTripsForm
        & render to the template
        """

        searched_date = self.get_searched_date()
        naive_searched_date = datetime.strptime(searched_date, "%Y-%m-%d")
        gte_dates = self.trips_matched_or_post_date(searched_date)
        lt_dates = self.trips_preceding_date(searched_date)

        # Find the trip closest to searched_date and make timezone naive
        if gte_dates:
            gte_date = gte_dates[0]
            naive_gte_date = self.make_timezone_naive(gte_date)
            if lt_dates:
                lt_date = lt_dates[0]
                naive_lt_date = self.make_timezone_naive(lt_date)

                if (
                    naive_gte_date - naive_searched_date
                    > naive_searched_date - naive_lt_date
                ):
                    default_selected = lt_date
                else:
                    default_selected = gte_date

            else:
                default_selected = gte_date

        elif lt_dates:
            lt_date = lt_dates[0]
            default_selected = lt_date

        else:
            messages.error(
                request,
                "Sorry, there are no dates currently available for the"
                "selected destination.",
            )

        trips = self.get_queryset()
        form = self.form_class(
            trips=trips,
            initial={
                "trip_date": default_selected,
            },
        )
        return render(request, self.template_name, {"form": form})

class ConfirmTripView(View):
    """ A view to confirm booking request """

    template_name = ''
    form_class = DateChoiceForm

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

def booking_details(request):
    """ A view to collect all booking details needed for booking """

    context = {}
    template = ""
    return render(request, template, context)
