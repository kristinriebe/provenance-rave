from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
#from django.template import loader
from django.core.urlresolvers import reverse
from django.views import generic

from .models import Activity, Entity, Agent, Used, WasGeneratedBy
from .models import WasAssociatedWith, WasAttributedTo, HadMember, WasDerivedFrom
from .models import RaveObsids

import json
from django.http import JsonResponse
from braces.views import JSONResponseMixin
from django.db.models.fields.related import ManyToManyField
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
#from rest_framework.renderers import XMLRenderer
from .serializers import ActivitySerializer, EntitySerializer, ProvenanceSerializer
from .forms import ObservationIdForm

from rest_framework.response import Response

import sys # just for debugging
import utils

def to_dict(instance):
    """
    Convert a model instance to a Python dictionary.
    Similar to Django's model_to_dict, but includes also non-editable fields.
    Also many-to-many fields are taken into account.
    """

    options = instance._meta
    data = {}
    for f in options.concrete_fields + options.many_to_many:
        if isinstance(f, ManyToManyField):
            if instance.pk is None:
                data[f.name] = []
            else:
                data[f.name] = list(f.value_from_object(instance).values_list('pk', flat=True))
        else:
            data[f.name] = f.value_from_object(instance)
    return data


class IndexView(generic.ListView):
    template_name = 'provapp/index.html'
    context_object_name = 'activity_list'

    def get_queryset(self):
        """Return the activities (at most 1000, ordered by startTime)."""
        return Activity.objects.order_by('-startTime')[:1000]


class ActivitiesView(generic.ListView):
    template_name = 'provapp/activities.html'
    context_object_name = 'activity_list'

    def get_queryset(self):
        """Return the activities (at most 1000, ordered by startTime)."""
        return Activity.objects.order_by('-startTime')[:1000]


class ActivityDetailView(generic.DetailView):
    model = Activity

    def get_context_data(self, **kwargs):
        context = super(ActivityDetailView, self).get_context_data(**kwargs)
        context['used_list'] = Used.objects.all()[:]
        context['wasGeneratedBy_list'] = WasGeneratedBy.objects.all()[:]
        context['wasAssociatedWith_list'] = WasAssociatedWith.objects.all()[:]
        context['wasAttributedTo_list'] = WasAttributedTo.objects.all()[:]
        return context


# simple json view, using just a function:
def myjson(request, activity_id):
    activity = get_object_or_404(Activity, pk=activity_id)
    #return HttpResponse(json.dumps(data), content_type='application/json')
    #activity_dict = {'id': activity.id, 'label': activity.label, 'type': activity.type, 'description': activity.description}
    activity_dict = to_dict(activity)
    return JsonResponse(activity_dict)


def graphjson(request, activity_id):
    activity = get_object_or_404(Activity, pk=activity_id)
    #return HttpResponse(json.dumps(data), content_type='application/json')
    #activity_dict = {'id': activity.id, 'label': activity.label, 'type': activity.type, 'description': activity.description}
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


# class-based view for json-response:
class ActivityDetailJsonView(JSONResponseMixin, generic.DetailView):
    model = Activity
    #json_dumps_kwargs = {u"indent": 2}

    def get(self, request, *args, **kwargs):
        activity = self.get_object() # wrap in try/except??? (404 error)
        # convert model to dictionary, cannot use built-in model_to_dict, since
        # this would ignore non-editable fields!
        # Could also use stuff from Django-Rest probably
        activity_dict = to_dict(activity)
        return self.render_json_response(activity_dict)

        # alternative with Django-Restframework (no need for JSONResponseMixin):
        # (should then have one serializer for each model!)
        #if request.method == 'GET':
        #    serializer = ActivitySerializer(activity)
        #return MyJsonResponse(serializer.data)

        # another idea: write own JSON-mixin etc.

# helper class for serializing into json, if using Django-Restframework
class MyJsonResponse(HttpResponse):
    """
    Http Response with JSON content
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(MyJsonResponse, self).__init__(content, **kwargs)


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



#class ActivityDetailJsonView(generic.ListView):
 #   template_name = 'provapp/activity_detail_json.html'
 #   model = Activity
 #   context_object_name = 'activity_json'
 #
 #   def get_queryset(self):
 #       return  HttpResponse(Activity.getjson, content_type='application/json')

    #def get_queryset(self):
    #    return Activity.objects.order_by('-startTime')[:1000]

    # def datatree(datadict, datacomponent):
    #     datadict['name'] = datacomponent.name

    #     if datacomponent.createdFromActivity:
    #         activity = datacomponent.createdFromActivity
    #         actdict = {}
    #         actdict['name'] = activity.name


    #         # append activity to datacomponent
    #         actlist = []
    #         actlist.append(actdict)
    #         datadict['children'] = actlist


    #         # get all inputs as dict.
    #         inputlist = activity.inputdata.all()
    #         childlist = []
    #         for dc in inputlist:
    #         #for dc in datacomponent.createdFromActivity.inputdata.all():
    #             inputdata = {}
    #             #inputdata['name'] = dc.name

    #             datatree(inputdata, dc)

    #             childlist.append(inputdata)

    #         # append all inputs to activity
    #         actdict['children'] = childlist
    #     else:
    #         pass

    #     return datadict


class GraphView(generic.ListView):
    """ Create the full provenance-graph needed for d3js or similar here """
    pass

    def get_queryset(self):
        return Activity.objects.order_by('-id')


class EntitiesView(generic.ListView):
    template_name = 'provapp/entities.html'
    context_object_name = 'entity_list'

    def get_queryset(self):
        """Return the entities (at most 1000, ordered by name)."""
        return Entity.objects.order_by('-name')[:1000]


class EntityDetailView(generic.DetailView):
    model = Entity


class AgentsView(generic.ListView):
    template_name = 'provapp/agents.html'
    context_object_name = 'agent_list'

    def get_queryset(self):
        """Return the agents (at most 1000, ordered by name)."""
        return Agent.objects.order_by('-name')[:1000]


class AgentDetailView(generic.DetailView):
    model = Agent


# simple prov-n view, using just a function:
def provn(request):
    activity_list = Activity.objects.order_by('-startTime')[:]
    entity_list = Entity.objects.order_by('-name')[:]
    agent_list = Agent.objects.order_by('-name')[:]
    used_list = Used.objects.order_by('-id')[:]
    wasGeneratedBy_list = WasGeneratedBy.objects.order_by('-id')[:]
    wasAssociatedWith_list = WasAssociatedWith.objects.order_by('-id')[:]
    wasAttributedTo_list = WasAttributedTo.objects.order_by('-id')[:]
    #return JsonResponse(activity_dict)
    #return render(request, 'provapp/activities.html', {'activity_list': activity_list})

    provstr = "document\n"
    for a in activity_list:
        provstr = provstr + "activity(" + a.id + ", " + str(a.startTime) + ", " + str(a.endTime) + ", [prov:type = '" + a.type + "', prov:name = '" + a.name + "', prov:description = '" + a.description + "']),\n"

    for e in entity_list:
        provstr = provstr + "entity(" + e.id + ", [prov:type = '" + e.type + "', prov:name = '" + e.name + "', prov:description = '" + e.description + "']),\n"

    for ag in agent_list:
        provstr = provstr + "agent(" + ag.id + ", [prov:type = '" + ag.type + "', prov:name = '" + ag.name + "', prov:description = '" + ag.description + "']),\n"

    for u in used_list:
        provstr = provstr + "used(" + u.activity.id + ", " + u.entity.id + ", [id = '" + str(u.id) + "', prov:role = '" + u.role + "']),\n"

    for wg in wasGeneratedBy_list:
        provstr = provstr + "wasGeneratedBy(" + wg.entity.id + ", " + wg.activity.id + ", [id = '" + str(wg.id) + "', prov:role = '" + wg.role + "']),\n"

    for wa in wasAssociatedWith_list:
        provstr = provstr + "wasAssociatedWith(" + wa.activity.id + ", " + wa.agent.id + ", [id = '" + str(wa.id) + "', prov:role = '" + wa.role + "']),\n"

    for wa in wasAttributedTo_list:
        provstr = provstr + "wasAttributedTo(" + wa.entity.id + ", " + wa.agent.id + ", [id = '" + str(wa.id) + "', prov:role = '" + wa.role + "']),\n"

    provstr += "endDocument"

    return HttpResponse(provstr, content_type='text/plain')

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
    return render(request, 'provapp/graph.html', {})


def fullgraphjson(request):
    #activity = get_object_or_404(Activity, pk=activity_id)
    #return HttpResponse(json.dumps(data), content_type='application/json')
    #activity_dict = {'id': activity.id, 'label': activity.label, 'type': activity.type, 'description': activity.description}
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
                else:
                    return HttpResponseRedirect('/provapp/' + str(entity.id) + '/detail')

            except ValueError:
                form = ObservationIdForm(request.POST)
        else:
            #print form.errors # or add_error??
            pass

    # if a GET (or any other method) we'll create a blank form
    else:
        form = ObservationIdForm()

    return render(request, 'provapp/observationId.html', {'form': form})


def provbasic(request, observation_id):
    entity = get_object_or_404(Entity, pk=observation_id)
    return render(request, 'provapp/provdetail.html', {'entity': entity})

def provbasicjson(request, observation_id):

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

    prov = utils.find_entity_basic_graph(entity, prov)

    #print "prov: ", prov

    prov_dict = {"nodes": prov['nodes_dict'], "links": prov['links_dict']}

    return JsonResponse(prov_dict)


def provdetail(request, observation_id):
    entity = get_object_or_404(Entity, pk=observation_id)

    return render(request, 'provapp/provdetail.html', {'entity': entity})


def provdetailjson(request, observation_id):

    entity = get_object_or_404(Entity, pk=observation_id)
    #print "entity: ", entity
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

    prov = utils.find_entity_detail_graph(entity, prov)

    #print "prov: ", prov

    prov_dict = {"nodes": prov['nodes_dict'], "links": prov['links_dict']}

    return JsonResponse(prov_dict)


def provdal_obsid(request):

    # TODO: use &format=... in url!
    for key, value in request.GET.items():
        print key, value
    observation_id = request.GET.get('ID') #default: None
    step = request.GET.get('STEP', 'LAST') # can be LAST or FIRST
    format = request.GET.get('FORMAT', 'PROVN') # can be PROVN, PROVJSON, VOTABLE
    model = request.GET.get('COMPLIANCE', 'IVOA')  # one of IVOA, W3C (or None?)

    try:
        entity = Entity.objects.get(id=observation_id)
    except Entity.DoesNotExist:
        entity = None
        #return HttpResponse(provstr, content_type='text/plain')

    prefix = {
        "rave": "http://www.rave-survey.org/prov/",
        "voprov": "http://www.ivoa.net/documents/ProvenanceDM/voprov/"
    }

    prov = {
        'prefix': prefix,
        'activity': {},
        'entity': {},
        'agent': {},
        'used': {},
        'wasGeneratedBy': {},
        'wasAssociatedWith': {},
        'wasAttributedTo': {},
        'hadMember': {},
        'wasDerivedFrom': {}
    }

    # store current entity in dict:
    if entity is not None:
        prov['entity'][entity.id] = entity

        # search for further provenance:
        prov = utils.find_entity(entity, prov)

    # The prov dictionary now contains the complete provenance information,
    # in the form of querysets. First serialize them, then render in the
    # desired format.

    # write provenance information in desired format:
    if format == 'PROVN':
        # TODO: write a provn-renderer for this
        provstr = "document\n"
        for p_id, p in prov['prefix'].iteritems():
            provstr = provstr + "prefix %s <%s>" % (p_id, p)

        for a_id, a in prov['activity'].iteritems():
            provstr = provstr + "activity(" + a.id + ", " + str(a.startTime) + ", " + str(a.endTime) + ", [voprov:type = '" + a.type + "', voprov:name = '" + a.name + "', voprov:annotation = '" + a.description + "']),\n"

        for e_id, e in prov['entity'].iteritems():
            provstr = provstr + "entity(" + e.id + ", [voprov:type = '" + e.type + "', voprov:name = '" + e.name + "', voprov:annotation = '" + e.description + "']),\n"

        for ag_id, ag in prov['agent'].iteritems():
            provstr = provstr + "agent(" + ag.id + ", [voprov:type = '" + ag.type + "', voprov:name = '" + ag.name + "', voprov:annotation = '" + ag.description + "']),\n"

        for u_id, u in prov['used'].iteritems():
            provstr = provstr + "used(" + u.activity.id + ", " + u.entity.id + ", [id = '" + str(u.id) + "', voprov:role = '" + u.role + "']),\n"

        for wg_id, wg in prov['wasGeneratedBy'].iteritems():
            provstr = provstr + "wasGeneratedBy(" + wg.entity.id + ", " + wg.activity.id + ", [id = '" + str(wg.id) + "', voprov:role = '" + wg.role + "']),\n"

        for wa_id, wa in prov['wasAssociatedWith'].iteritems():
            provstr = provstr + "wasAssociatedWith(" + wa.activity.id + ", " + wa.agent.id + ", [id = '" + str(wa.id) + "', voprov:role = '" + wa.role + "']),\n"

        for wa_id, wa in prov['wasAttributedTo'].iteritems():
            provstr = provstr + "wasAttributedTo(" + wa.entity.id + ", " + wa.agent.id + ", [id = '" + str(wa.id) + "', voprov:role = '" + wa.role + "']),\n"

        for h_id, h in prov['hadMember'].iteritems():
            provstr = provstr + "hadMember(" + h.entity.id + ", " + h.entity.id + ", [id = '" + str(h.id) + "']),\n"

        for wd_id, wd in prov['wasDerivedFrom'].iteritems():
            provstr = provstr + "wasDerivedFrom(" + wd.entity.id + ", " + wd.entity.id + ", [id = '" + str(wd.id) + "']),\n"

        provstr += "endDocument"
        return HttpResponse(provstr, content_type='text/plain; charset=utf-8')


    elif format == 'PROVJSON':
        #votable = VOTableRenderer().render(data, votable_meta=votable_meta, prettyprint=False)

        # test serializers:
        #json_str = serializers.serialize('json', prov['entity_list']) #, fields=('name',''))
        # => works!

        # convert querysets to serialized python objects
        serializer = ProvenanceSerializer(prov) # => works!
        data = serializer.data

        json_str = json.dumps(data,
                sort_keys=True,
                indent=4
               )
       # => works!

#        json_str = JSONRenderer().render(serializer.data)
        return HttpResponse(json_str, content_type='text/json; charset=utf-8')

    else:
        # format is not known, return error
        provstr = "Sorry, unknown format %s was requested, cannot handle this." % format
    return HttpResponse(provstr, content_type='text/plain; charset=utf-8')


#def detail(request, activity_id):
#    activity = get_object_or_404(Activity, pk=activity_id)
#    return render(request, 'provapp/detail.html', {'activity': activity})

#def activities(request):
#    #activity_list = get_object_or_404(Activity.objects.order_by('-startTime')[:]
#    #return render(request, 'provapp/activities.html', {'activity_list': activity_list})
#    activity_list = Activity.objects.order_by('-startTime')[:]
#    return render(request, 'provapp/activities.html', {'activity_list': activity_list})

#def entities(request):
#    entity_list = Entity.objects.order_by('-label')[:]
#    return render(request, 'provapp/entities.html', {'entity_list': entity_list})

#def agents(request):
#    agent_list = Agent.objects.order_by('-label')[:]
#    return render(request, 'provapp/agents.html', {'agent_list': agent_list})
