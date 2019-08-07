from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader

from .forms import SimulationSettingsForm

import time


def submit_sim_params(request):
    if request.method == 'GET':
        form = SimulationSettingsForm()
    elif request.method == 'POST':
        form = SimulationSettingsForm(request.POST)
        if form.is_valid():
            cleaned_form_data = form.cleaned_data
            print(cleaned_form_data)
            return redirect(reverse('sim_process'))

    template = loader.get_template('lws_web_host/index.html')

    context = {
        'form': form,
    }
    return HttpResponse(template.render(context, request))


def sim_process(sim_params):
    time.sleep(5)
    return redirect('sim_result_view')


def sim_result_view(request):
    return HttpResponse("sim_result view")
