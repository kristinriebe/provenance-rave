import sys # just for debugging
import json
from datetime import datetime

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
#from django.template import loader
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.views import generic
from django.http import JsonResponse
from django.db.models.fields.related import ManyToManyField
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt

from braces.views import JSONResponseMixin

#from rest_framework.renderers import XMLRenderer
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework import viewsets

import utils

from .models import (
    Activity,
    Entity,
    Agent,
    Used,
    WasGeneratedBy,
    WasAssociatedWith,
    WasAttributedTo,
    HadMember,
    HadStep,
    WasDerivedFrom,
    WasInformedBy,
    ActivityFlow,
    Collection,
    #Bundle,
    RaveObsids
)

from .serializers import (
    ActivitySerializer,
    EntitySerializer,
    AgentSerializer,
    UsedSerializer,
    WasGeneratedBySerializer,
    WasAssociatedWithSerializer,
    WasAttributedToSerializer,
    HadMemberSerializer,
    WasDerivedFromSerializer,
    WasInformedBySerializer,
    CollectionSerializer,
    W3CProvenanceSerializer,
    VOProvenanceSerializer,
    ProvenanceGraphSerializer
)

from .renderers import PROVNRenderer, PROVJSONRenderer

from .forms import ObservationIdForm, ProvDalForm


class IndexView(generic.ListView):
    template_name = 'provapp/index.html'
    context_object_name = 'activity_list'

    def get_queryset(self):
        """Return the activities (at most 1000, ordered by startTime)."""
        return Activity.objects.order_by('-startTime')[:1000]


class ActivityViewSet(viewsets.ModelViewSet):
    serializer_class = ActivitySerializer
    queryset = Activity.objects.all()

class EntityViewSet(viewsets.ModelViewSet):
    serializer_class = EntitySerializer
    queryset = Entity.objects.all()

class AgentViewSet(viewsets.ModelViewSet):
    serializer_class = AgentSerializer
    queryset = Agent.objects.all()

class UsedViewSet(viewsets.ModelViewSet):
    serializer_class = UsedSerializer
    queryset = Used.objects.all()

class WasGeneratedByViewSet(viewsets.ModelViewSet):
    serializer_class = WasGeneratedBySerializer
    queryset = WasGeneratedBy.objects.all()

class WasAssociatedWithViewSet(viewsets.ModelViewSet):
    serializer_class = WasAssociatedWithSerializer
    queryset = WasAssociatedWith.objects.all()

class WasAttributedToViewSet(viewsets.ModelViewSet):
    serializer_class = WasAttributedToSerializer
    queryset = WasAttributedTo.objects.all()

class HadMemberViewSet(viewsets.ModelViewSet):
    serializer_class = HadMemberSerializer
    queryset = HadMember.objects.all()

class WasDerivedFromViewSet(viewsets.ModelViewSet):
    serializer_class = WasDerivedFromSerializer
    queryset = WasDerivedFrom.objects.all()

# class ActivityFlowViewSet(viewsets.ModelViewSet):
#     serializer_class = ActivityFlowSerializer
#     queryset = ActivityFlow.objects.all()

class CollectionViewSet(viewsets.ModelViewSet):
    serializer_class = CollectionSerializer
    queryset = Collection.objects.all()

def activitygraphjson(request, activity_id):
    activity = get_object_or_404(Activity, pk=activity_id)
    #return HttpResponse(json.dumps(data), content_type='application/json')
    #activity_dict = {'id': activity.id, 'label': activity.label, 'type': activity.type, 'annotation': activity.annotation}
    #activity_dict = to_dict(activity)

    used_list = Used.objects.all()
    wasGeneratedBy_list = WasGeneratedBy.objects.all()
    wasAssociatedWith_list = WasAssociatedWith.objects.all()

    nodes_dict = []
    nodes_dict.append({"name": activity.name, "type": "activity"})
    count_nodes = 0
    count_act = 0

    links_dict = []
    count_link = 0

    for u in used_list:
        if u.activity.id == activity_id:
            # add node
            nodes_dict.append({"name": "%s" % u.entity.name, "type": "entity"})
            count_nodes = count_nodes + 1

            # and add link (source, target, value)
            links_dict.append({"source": count_act, "target": count_nodes, "value": 0.2, "type": "used"})
            count_link = count_link + 1


    for w in wasGeneratedBy_list:
        if w.activity.id == activity_id:
            # add node
            nodes_dict.append({"name": "%s" % w.entity.name, "type": "entity"})
            count_nodes = count_nodes + 1

            # and add link (source, target, value)
            links_dict.append({"source": count_nodes, "target": count_act, "value": 0.2, "type": "wasGeneratedBy"})
            count_link = count_link + 1

    for w in wasAssociatedWith_list:
        if w.activity.id == activity_id:
            # add node
            nodes_dict.append({"name": "%s" % w.agent.name, "type": "agent"})
            count_nodes = count_nodes + 1

            # and add link (source, target, value)
            links_dict.append({"source": count_act, "target": count_nodes, "value": 0.5, "type": "wasAssociatedWith"})
            count_link = count_link + 1

    prov_dict = {"nodes": nodes_dict, "links": links_dict}

    return JsonResponse(prov_dict)


class ActivityDetailXmlView(generic.DetailView):
    model = Activity
    #json_dumps_kwargs = {u"indent": 2}

    def get(self, request, *args, **kwargs):
        activity = self.get_object() # wrap in try/except??? (404 error)
        #serializer = ActivitySerializer(activity)
        #return MyJsonResponse(serializer.data)
        #serializers.deserialize("xml", data, ignorenonexistent=True)

        data = serializers.serialize('xml', [ activity ] )
        # How to use not all, but only this currently selected activity???

        #activity_dict = to_dict(activity)
        return HttpResponse(data, content_type="application/xml")


def convert_to_dict_querysets(listqueryset):

    objdict = {}
    for q in listqueryset:
        objdict[q.id] = q

    return objdict


# simple prov-n view of everything
def allprov(request, format):

    # first store everything in a prov-dictionary
    prefix = {
        "rave": "http://www.rave-survey.org/prov/",
        "voprov": "http://www.ivoa.net/documents/ProvenanceDM/voprov/",
        "org": "http://www.ivoa.net/documents/ProvenanceDM/voprov/org/",
        "vo": "http://www.ivoa.net/documents/ProvenanceDM/voprov/vo",
        "prov": "http://www.w3.org/ns/prov#",  # defined by default
        "xsd": "http://www.w3.org/2000/10/XMLSchema#"  # defined by default
    }

    prov = {
        'prefix': prefix,
        'activity': convert_to_dict_querysets(Activity.objects.all()),
        'entity': convert_to_dict_querysets(Entity.objects.all()),
        'agent': convert_to_dict_querysets(Agent.objects.all()),
        'used': convert_to_dict_querysets(Used.objects.all()),
        'wasGeneratedBy': convert_to_dict_querysets(WasGeneratedBy.objects.all()),
        'wasAssociatedWith': convert_to_dict_querysets(WasAssociatedWith.objects.all()),
        'wasAttributedTo': convert_to_dict_querysets(WasAttributedTo.objects.all()),
        'hadMember': convert_to_dict_querysets(HadMember.objects.all()),
        'wasDerivedFrom': convert_to_dict_querysets(WasDerivedFrom.objects.all())
    }

    #return JsonResponse(activity_dict)
    #return render(request, 'provapp/activities.html', {'activity_list': activity_list})

    # serialize it (W3C):
    serializer = W3CProvenanceSerializer(prov)
    data = serializer.data

    # write provenance information in desired format:
    if format == 'PROV-N':
        provstr = PROVNRenderer().render(data)
        return HttpResponse(provstr, content_type='text/plain; charset=utf-8')

    elif format == 'PROV-JSON':
        json_str = PROVJSONRenderer().render(data)
        return HttpResponse(json_str, content_type='application/json; charset=utf-8')

    else:
        # format is not known, return error
        provstr = "Sorry, unknown format %s was requested, cannot handle this." % format

    return HttpResponse(provstr, content_type='text/plain; charset=utf-8')


def prettyprovn(request):
    activity_list = Activity.objects.order_by('-startTime')[:]
    entity_list = Entity.objects.order_by('-name')[:]
    agent_list = Agent.objects.order_by('-name')[:]
    used_list = Used.objects.order_by('-id')[:]
    wasGeneratedBy_list = WasGeneratedBy.objects.order_by('-id')[:]
    wasAssociatedWith_list = WasAssociatedWith.objects.order_by('-id')[:]
    wasAttributedTo_list = WasAttributedTo.objects.order_by('-id')[:]
    #return JsonResponse(activity_dict)
    return render(request, 'provapp/provn.html',
                 {'activity_list': activity_list,
                  'entity_list': entity_list,
                  'agent_list': agent_list,
                  'used_list': used_list,
                  'wasGeneratedBy_list': wasGeneratedBy_list,
                  'wasAssociatedWith_list': wasAssociatedWith_list,
                  'wasAttributedTo_list': wasAttributedTo_list
                 })


def graph(request):
    return render(request, 'provapp/graph.html', {'url': 'graphjson'})


def fullgraphjson(request):
    #activity = get_object_or_404(Activity, pk=activity_id)
    #return HttpResponse(json.dumps(data), content_type='application/json')
    #activity_dict = {'id': activity.id, 'label': activity.label, 'type': activity.type, 'annotation': activity.annotation}
    #activity_dict = to_dict(activity)


    activity_list = Activity.objects.all()
    entity_list = Entity.objects.all()
    agent_list = Agent.objects.all()

    used_list = Used.objects.all()
    wasGeneratedBy_list = WasGeneratedBy.objects.all()
    wasAssociatedWith_list = WasAssociatedWith.objects.all()
    wasAttributedTo_list = WasAttributedTo.objects.all()
    hadMember_list = HadMember.objects.all()

    nodes_dict = []
    count_nodes = 0
    count_act = 0

    links_dict = []
    count_link = 0

    map_activity_ids = {}
    map_entity_ids = {}
    map_agent_ids = {}


    for a in activity_list:
        nodes_dict.append({"name": a.name, "type": "activity"})
        map_activity_ids[a.id] = count_nodes
        count_nodes = count_nodes + 1

    for e in entity_list:
        nodes_dict.append({"name": e.name, "type": "entity"})
        map_entity_ids[e.id] = count_nodes
        count_nodes = count_nodes + 1

    for ag in agent_list:
        nodes_dict.append({"name": ag.name, "type": "agent"})
        map_agent_ids[ag.id] = count_nodes
        count_nodes = count_nodes + 1

    # add links (source, target, value)
    for u in used_list:
        links_dict.append({"source": map_activity_ids[u.activity.id], "target": map_entity_ids[u.entity.id], "value": 0.5, "type": "used"})
        count_link = count_link + 1

    for w in wasGeneratedBy_list:
        links_dict.append({"source": map_entity_ids[w.entity.id], "target": map_activity_ids[w.activity.id], "value": 0.5, "type": "wasGeneratedBy"})
        count_link = count_link + 1

    for w in wasAssociatedWith_list:
        links_dict.append({"source": map_activity_ids[w.activity.id], "target": map_agent_ids[w.agent.id], "value": 0.2, "type": "wasAssociatedWith"})
        count_link = count_link + 1

    for w in wasAttributedTo_list:
        links_dict.append({"source": map_entity_ids[w.entity.id], "target": map_agent_ids[w.agent.id], "value": 0.2, "type": "wasAttributedTo"})
        count_link = count_link + 1

    for h in hadMember_list:
        s =  map_entity_ids[h.collection_id]
        #print >>sys.stderr, 'h.collection_id, h.entity_id: ', h.collection_id, ", '"+h.entity_id+"'"
        t = map_entity_ids[h.entity_id]
        #print "map_entity_ids[h.collection_id]"
        #links_dict.append({"source": map_entity_ids[h.collection_id], "target": map_entity_ids[h.entity_id], "value": 0.2, "type": "hadMember"})
        links_dict.append({"source": s, "target": t, "value": 0.2, "type": "hadMember"})
        count_link = count_link + 1


    prov_dict = {"nodes": nodes_dict, "links": links_dict}

    return JsonResponse(prov_dict)


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
                print "detail: ", detail
                #print "from obsid-table: ", obsid

                #if obsid: -- should we check this??
                # get the entity from entity table:
                entity = Entity.objects.get(name=form.cleaned_data['observation_id'])

                if detail == 'basic':
                    return HttpResponseRedirect('/provapp/' + str(entity.id) + '/basic')
                elif detail == 'detailed':
                    return HttpResponseRedirect('/provapp/' + str(entity.id) + '/detail')
                else:
                    return HttpResponseRedirect('/provapp/' + str(entity.id) + '/all')

            except ValueError:
                form = ObservationIdForm(request.POST)
        else:
            #print form.errors # or add_error??
            pass

    # if a GET (or any other method) we'll create a blank form
    else:
        form = ObservationIdForm()

    return render(request, 'provapp/observationId.html', {'form': form})


def observationid_detail(request, observation_id, detail_flag):
    entity = get_object_or_404(Entity, pk=observation_id)

    return render(request, 'provapp/observationid_detail.html', {'entity': entity, 'url': 'graphjson'})


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

    prov = utils.find_entity_graph(entity, prov, collection=collection)

    prov_dict = {"nodes": prov['nodes_dict'], "links": prov['links_dict']}

    return JsonResponse(prov_dict)


def provdal_form(request):

    if request.method == 'POST':
        form = ProvDalForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
        # process the data in form.cleaned_data as required
            try:
                obj_id = form.cleaned_data['obj_id']
                step = form.cleaned_data['step_flag']
                format = form.cleaned_data['format']
                compliance = form.cleaned_data['model']

                return HttpResponseRedirect(reverse('provapp:provdal')+"?ID=%s&STEP=%s&FORMAT=%s&MODEL=%s" % (str(obj_id), str(step), str(format), str(compliance)))

            except ValueError:
                form = ProvDalForm(request.POST)
        else:
            #print form.errors # or add_error??
            pass

    # if a GET (or any other method) we'll create a blank form
    else:
        form = ProvDalForm()

    return render(request, 'provapp/provdalform.html', {'form': form})


def provdal(request):

    # entity_id = request.GET.get('ID') #default: None
    # There can be more than one ID given, so:
    id_list = request.GET.getlist('ID')
    step_flag = request.GET.get('STEP', 'LAST') # can be LAST or ALL
    format = request.GET.get('FORMAT', 'PROV-N') # can be PROV-N, PROV-JSON, VOTABLE
    model = request.GET.get('MODEL', 'IVOA')  # one of IVOA, W3C (or None?)

    if format == 'GRAPH':
        ids = ''
        for i in id_list:
            ids += 'ID=%s&' % i
        return render(request, 'provapp/provdal_graph.html',
            {'url': reverse('provapp:provdal') + "?%sSTEP=%s&FORMAT=GRAPH-JSON&MODEL=%s" % (ids, str(step_flag), str(model))})

    # check step_flag, store as 'follow' for provenance functions
    if step_flag == "ALL":
        # will search for further provenance, recursively
        follow = True
    elif step_flag == "LAST":
        # will just go back one step (backwards in time)
        follow = False
    else:
        # raise error: not supported
        raise ValidationError(
            'Invalid value: %(value)s is not supported',
            code='invalid',
            params={'value': step_flag},
        )

    prefix = {
        "rave": "http://www.rave-survey.org/prov/",
        "voprov": "http://www.ivoa.net/documents/ProvenanceDM/voprov/",
        "org": "http://www.ivoa.net/documents/ProvenanceDM/voprov/org/",
        "vo": "http://www.ivoa.net/documents/ProvenanceDM/voprov/vo",
        "prov": "http://www.w3.org/ns/prov#",  # defined by default
        "xsd": "http://www.w3.org/2000/10/XMLSchema#"  # defined by default
    }

    prov = {
        'prefix': prefix,
        'activity': {},
        'activityFlow': {},
        'entity': {},
        'collection': {},  # not used, yet, stored with entities
        'agent': {},
        'used': {},
        'wasGeneratedBy': {},
        'wasAssociatedWith': {},
        'wasAttributedTo': {},
        'hadMember': {},
        'wasDerivedFrom': {},
        'hadStep': {},
        'wasInformedBy': {}
    }

    # Note: even if collection class is used, Entity.objects.all() still contains all entities
    for obj_id in id_list:

        try:
            entity = Entity.objects.get(id=obj_id)
            # store current entity in dict and search for provenance:
            prov['entity'][entity.id] = entity
            prov = utils.find_entity(entity, prov, follow=follow)
        except Entity.DoesNotExist:
            pass
            # do not return, just continue with other ids
            # (and if none of them exists, return empty provenance record)

        try:
            activity = Activity.objects.get(id=obj_id)
            # or store current activity and search for its provenance
            activity_type = utils.get_activity_type(obj_id)

            prov[activity_type][activity.id] = activity
            prov = utils.find_activity(activity, prov, follow=follow)
        except Activity.DoesNotExist:
            pass


    # The prov dictionary now contains the complete provenance information,
    # for all given entity ids,
    # in the form of a dictionary of querysets. First serialize them according to
    # the specified model.
    if model == "W3C":
        serializer = W3CProvenanceSerializer(prov)
    elif model == "IVOA":
        serializer = VOProvenanceSerializer(prov)
    else:
        # raise error: not supported
        raise ValidationError(
           'Invalid value: %(value)s is not supported',
            code='invalid',
            params={'value': model},
        )

    data = serializer.data

    # Render provenance information in desired format:
    if format == 'PROV-N':
        provstr = PROVNRenderer().render(data)
        return HttpResponse(provstr, content_type='text/plain; charset=utf-8')

    elif format == 'PROV-JSON':

        json_str = PROVJSONRenderer().render(data)
        return HttpResponse(json_str, content_type='application/json; charset=utf-8')

    elif format == "GRAPH-JSON":
        # need to re-structure the serialized data
        serializer = ProvenanceGraphSerializer(prov) ## should use W3C or IVOA formatted data-structure here!!
        prov_dict = serializer.data
        return JsonResponse(prov_dict)

    else:
        # format is not known, return error
        provstr = "Sorry, unknown format %s was requested, cannot handle this." % format
        return HttpResponse(provstr, content_type='text/plain; charset=utf-8')
