# -*- coding: utf-8 -*-

from django import http
from django.views.generic.detail import SingleObjectMixin
from django.views.generic import CreateView, View
from django.shortcuts import render, get_object_or_404
from braces.views import LoginRequiredMixin, UserFormKwargsMixin
from olwidget.widgets import InfoLayer, Map, InfoMap

from forms import LocationAddForm
from models import Zone, Location


def zone_detail(request, slug):
    zone = get_object_or_404(Zone, slug=slug)

    worldborders = zone.worldborder_set.all()
    locations = zone.location_set.all()

    worldborders_layer = InfoLayer([(wb.poly_simplify, wb.name_1) for wb in worldborders])
    locations_layer = InfoLayer([(l.point, l.map_html) for l in locations])

    this_map = Map([worldborders_layer, locations_layer],
                   {'layers': ['google.streets', 'google.satellite', 'google.hybrid'],
                    'map_div_style': {'width': '570px', 'height': '400px'}})

    return render(request, 'world/zone_detail.html', {
        'zone': zone,
        'map': this_map,
    })


def location_detail(request, slug):
    location = get_object_or_404(Location, slug=slug)

    this_map = InfoMap([(location.point, location.map_html)],
                   {'layers': ['google.streets', 'google.satellite', 'google.hybrid'],
                    'map_div_style': {'width': '570px', 'height': '400px'}})


    return render(request, 'world/location_detail.html', {
        'location': location,
        'map': this_map,
    })

class LocationAddView(LoginRequiredMixin, UserFormKwargsMixin, CreateView):
    model = Location
    form_class = LocationAddForm
    template_name = 'world/location_add.html'

    def get_form_kwargs(self, **kwargs):
        kwargs = super(LocationAddView, self).get_form_kwargs()
        kwargs['zone'] = get_object_or_404(Zone, slug=self.kwargs['slug'])
        return kwargs


    def get_context_data(self, **kwargs):
        context = super(LocationAddView, self).get_context_data(**kwargs)
        context['zone'] = get_object_or_404(Zone, slug=self.kwargs['slug'])
        return context


class LocationValidateView(LoginRequiredMixin, SingleObjectMixin, View):
    model = Location

    def get(self, request, *args, **kwargs):
        location = self.get_object()
        location.validated_by.add(request.user)
        location.save()

        return http.HttpResponseRedirect(location.get_absolute_url())

