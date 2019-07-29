from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

from .forms import SimulationSettingsForm


def index(request):
    if request.method == 'GET':
        form = SimulationSettingsForm()
    elif request.method == 'POST':
        form = SimulationSettingsForm(request.POST)
        if form.is_valid():
            region = form.cleaned_data
            print(region)

    template = loader.get_template('lws_web_host/index.html')

    context = {
        'form' : form,
    }
    return HttpResponse(template.render(context, request))


