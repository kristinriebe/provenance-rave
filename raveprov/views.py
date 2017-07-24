# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.core.urlresolvers import reverse

from provapp.models import Entity
import provapp.utils

from .forms import ObservationIdForm
from .models import RaveObsids

def get_observationId(request):
    # Get the context from the request.
    #context = RequestContext(request)

    if request.method == 'POST':
        form = ObservationIdForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
        # process the data in form.cleaned_data as required
            try:
                #print form.cleaned_data
                #entity = Entity.objects.get(label=form.cleaned_data['observation_id'])
                #return HttpResponseRedirect('/provapp/provdetail/'+entity.id)

                obsid = RaveObsids.objects.get(rave_obs_id=form.cleaned_data['observation_id'])
                detail = form.cleaned_data['detail_flag']
                # print "detail: ", detail
                #print "from obsid-table: ", obsid

                #if obsid: -- should we check this??
                # get the entity from entity table:
                entity = Entity.objects.get(name=form.cleaned_data['observation_id'])

                if detail == 'basic':
                    detail_flag = 'basic'
                elif detail == 'detailed':
                    detail_flag = 'detail'
                else:
                    detail_flag = 'all'

                return HttpResponseRedirect(reverse('raveprov:observationid_detail', kwargs={'observation_id': str(entity.id), 'detail_flag': 'basic'}))

            except ValueError:
                form = ObservationIdForm(request.POST)
        else:
            #print form.errors # or add_error??
            pass

    # if a GET (or any other method) we'll create a blank form
    else:
        form = ObservationIdForm()

    return render(request, 'raveprov/observationId.html', {'form': form})


def observationid_detail(request, observation_id, detail_flag):
    entity = get_object_or_404(Entity, pk=observation_id)
    return render(request, 'raveprov/observationid_detail.html', {'entity': entity, 'url': 'graphjson'})


def observationid_detailjson(request, observation_id, detail_flag):

    entity = get_object_or_404(Entity, pk=observation_id)

    nodes_dict = []
    count_nodes = 0
    links_dict = []
    count_link = 0

    map_nodes_ids = {}
    prov = {
        'nodes_dict': nodes_dict,
        'links_dict': links_dict,
        'map_nodes_ids': map_nodes_ids,
        'count_nodes': count_nodes,
        'count_link': count_link
    }

    # put first entity into json:
    prov['nodes_dict'].append({'name': entity.name, 'type': 'entity'})
    prov['map_nodes_ids'][entity.id] = prov['count_nodes']
    prov['count_nodes'] = prov['count_nodes'] + 1

    if detail_flag == "basic":
        collection = "only"
    elif detail_flag == "detail":
        collection = "exclude"
    elif detail_flag == "all":
        collection = "include"
    else:
        # raise error: not supported
        raise ValidationError(
                'Invalid value: %(value)s is not supported',
                code='invalid',
                params={'value': detail_flag},
            )

    prov = provapp.utils.find_entity_graph(entity, prov, collection=collection)

    prov_dict = {"nodes": prov['nodes_dict'], "links": prov['links_dict']}

    return JsonResponse(prov_dict)
