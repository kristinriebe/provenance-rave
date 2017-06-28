from collections import OrderedDict

from rest_framework import serializers
from rest_framework.fields import SkipField, empty
from rest_framework.relations import PKOnlyObject

from django.db.models import Max

from .models import (
    Activity,
    Entity,
    Agent,
    Used,
    WasGeneratedBy,
    WasAssociatedWith,
    WasAttributedTo,
    HadMember,
    WasDerivedFrom,
    ActivityFlow,
    Collection,
    WasInformedBy,
    HadStep
)

# Define custom CharField to add attribute custom_field_name
class CustomCharField(serializers.CharField):

    def __init__(self, **kwargs):
        self.allow_blank = kwargs.pop('allow_blank', False)
        self.trim_whitespace = kwargs.pop('trim_whitespace', True)
        self.max_length = kwargs.pop('max_length', None)
        self.min_length = kwargs.pop('min_length', None)

        self.custom_field_name = kwargs.pop('custom_field_name', None)

        super(CustomCharField, self).__init__(**kwargs)
        if self.max_length is not None:
            message = self.error_messages['max_length'].format(max_length=self.max_length)
            self.validators.append(MaxLengthValidator(self.max_length, message=message))
        if self.min_length is not None:
            message = self.error_messages['min_length'].format(min_length=self.min_length)
            self.validators.append(MinLengthValidator(self.min_length, message=message))


# Define custom DateTimeField to add attribute custom_field_name
class CustomDateTimeField(serializers.DateTimeField):

    def __init__(self, format=empty, input_formats=None, default_timezone=None, *args, **kwargs):
        if format is not empty:
            self.format = format
        if input_formats is not None:
            self.input_formats = input_formats
        if default_timezone is not None:
            self.timezone = default_timezone

        self.custom_field_name = kwargs.pop('custom_field_name', None)

        super(CustomDateTimeField, self).__init__(*args, **kwargs)


# Define custom serializer class with some modifications
class NonNullCustomSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        """
        Object instance -> Dict of primitive datatypes.
        """
        # Overwrite this method from serializers.py, Serializer-class,
        # because I want to skip empty fields in serialisation and need qualified fieldnames
        ret = OrderedDict()
        fields = self._readable_fields

        for field in fields:
            try:
                attribute = field.get_attribute(instance)
            except SkipField:
                continue

            # Check, if there is a custom_field_name attribute.
            # If so (and it's not None), then use this instead of field name.
            # This is useful for namespaced fieldnames, e.g. "prov:label"
            field_name = field.field_name
            if hasattr(field, 'custom_field_name'):
                custom_field_name = field.custom_field_name
                if custom_field_name is not None:
                    field_name = custom_field_name

            # We skip `to_representation` for `None` values so that fields do
            # not have to explicitly deal with that case.
            #
            # For related fields with `use_pk_only_optimization` we need to
            # resolve the pk value.
            check_for_none = attribute.pk if isinstance(attribute, PKOnlyObject) else attribute
            if check_for_none is None:
                # skip this field, if it is none
                pass
            else:
                representation = field.to_representation(attribute)
                if representation is None:
                    # Do not seralize empty objects
                    continue
                if isinstance(representation, list) and not representation:
                    # Do not serialize empty lists
                    continue

                ret[field_name] = representation

        return ret


class ActivitySerializer(NonNullCustomSerializer):

    prov_id = CustomCharField(source='id', custom_field_name='prov:id')
    prov_label = CustomCharField(source='name', custom_field_name='prov:label')
    prov_type = CustomCharField(source='type', custom_field_name='prov:type')
    prov_description = CustomCharField(source='annotation', custom_field_name='prov:description')
    prov_startTime = CustomDateTimeField(source='startTime', custom_field_name='prov:startTime')
    prov_endTime = CustomDateTimeField(source='endTime', custom_field_name='prov:endTime')
    voprov_doculink = CustomCharField(source='doculink', custom_field_name='voprov:doculink')

    class Meta:
        model = Activity
        fields = ('prov_id', 'prov_label', 'prov_type', 'prov_description', 'prov_startTime', 'prov_endTime', 'voprov_doculink')
        # exclude id later on, when it will be used as key in the dictionary anyway
        # but still keep it here in the serializer


class EntitySerializer(NonNullCustomSerializer):

    prov_id = CustomCharField(source='id', custom_field_name='prov:id')
    prov_label = CustomCharField(source='name', custom_field_name='prov:label')
    prov_type = CustomCharField(source='type', custom_field_name='prov:type')
    prov_description = CustomCharField(source='annotation', custom_field_name='prov:description')
    voprov_rights = CustomCharField(source='rights', custom_field_name='voprov:rights')
    voprov_dataType = CustomCharField(source='dataType', custom_field_name='voprov:dataType')
    voprov_storageLocation = CustomCharField(source='storageLocation', custom_field_name='voprov:storageLocation')

    class Meta:
        model = Entity
        fields = ('prov_id', 'prov_label', 'prov_type', 'prov_description', 'voprov_rights', 'voprov_dataType', 'voprov_storageLocation')


class AgentSerializer(NonNullCustomSerializer):

    prov_id = CustomCharField(source='id', custom_field_name='prov:id')
    prov_type = CustomCharField(source='type', custom_field_name='prov:type')
    voprov_name = CustomCharField(source='name', custom_field_name='prov:label')
    voprov_email = CustomCharField(source='email', custom_field_name='voprov:email')
    prov_description = CustomCharField(source='annotation', custom_field_name='prov:description')

    class Meta:
        model = Agent
        fields = ('prov_id', 'voprov_name', 'prov_type', 'voprov_email', 'prov_description')


class UsedSerializer(NonNullCustomSerializer):

    prov_activity = CustomCharField(source='activity_id', custom_field_name='prov:activity')
    prov_entity = CustomCharField(source='entity_id', custom_field_name='prov:entity')
    prov_time = CustomDateTimeField(source='time', custom_field_name='prov:time')
    prov_role = CustomCharField(source='role', custom_field_name='prov:role')

    class Meta:
        model = Used
        fields = ('id', 'prov_activity', 'prov_entity', 'prov_time', 'prov_role')


class WasGeneratedBySerializer(NonNullCustomSerializer):

    prov_entity = CustomCharField(source='entity_id', custom_field_name='prov:entity')
    prov_activity = CustomCharField(source='activity_id', custom_field_name='prov:activity')
    prov_time = CustomDateTimeField(source='time', custom_field_name='prov:time')
    prov_role = CustomCharField(source='role', custom_field_name='prov:role')

    class Meta:
        model = WasGeneratedBy
        fields = ('id', 'prov_entity', 'prov_activity', 'prov_time', 'prov_role')


class WasAssociatedWithSerializer(NonNullCustomSerializer):

    class Meta:
        model = WasAssociatedWith
        fields = '__all__'


class WasAttributedToSerializer(NonNullCustomSerializer):

    # role is not allowed in W3C for wasAttributedTo, thus use voprov-namespace
    voprov_role = CustomCharField(source='role', custom_field_name='voprov:role')

    class Meta:
        model = WasAttributedTo
        fields = ('id', 'entity', 'agent', 'voprov_role')


class HadMemberSerializer(NonNullCustomSerializer):

    class Meta:
        model = HadMember
        fields = '__all__'


class WasDerivedFromSerializer(NonNullCustomSerializer):

    class Meta:
        model = WasDerivedFrom
        fields = '__all__'

class WasInformedBySerializer(NonNullCustomSerializer):

    class Meta:
        model = WasInformedBy
        fields = '__all__'

class CollectionSerializer(EntitySerializer):

    class Meta:
        model = Collection
        fields = ('prov_id', 'prov_label', 'prov_type', 'prov_description', 'voprov_rights', 'voprov_dataType', 'voprov_storageLocation')


class W3CProvenanceSerializer(serializers.Serializer):

    activity = serializers.SerializerMethodField()
    entity = serializers.SerializerMethodField()
    agent = serializers.SerializerMethodField()
    used = serializers.SerializerMethodField()
    wasGeneratedBy = serializers.SerializerMethodField()
    wasAssociatedWith = serializers.SerializerMethodField()
    wasAttributedTo = serializers.SerializerMethodField()
    hadMember = serializers.SerializerMethodField()
    wasDerivedFrom = serializers.SerializerMethodField()
    wasInformedBy = serializers.SerializerMethodField()
    prefix = serializers.SerializerMethodField()


    def get_prefix(self, obj):
        return obj['prefix']

    # get all the class instances serialized by their
    # corresponding serializer;
    # adjust the serialization, where necessary, for each item
    def get_activity(self, obj):
        activity = {}
        for a_id, a in obj['activity'].iteritems():
            data = ActivitySerializer(a).data
            activity[a_id] = data

        # add activities that are stored as activityFlow to
        # activities for W3C serialisation
        for a_id, a in obj['activityFlow'].iteritems():
            data = ActivitySerializer(a).data
            data['voprov:votype'] = 'voprov:activityFlow'
            activity[a_id] = data
        return activity

    def get_entity(self, obj):
        entity = {}
        for e_id, e in obj['entity'].iteritems():
            data = EntitySerializer(e).data
            entity[e_id] = data

        for e_id, e in obj['collection'].iteritems():
            data = CollectionSerializer(e).data
            entity[e_id] = data

        # create a plan for each activityFlow
        for a_id, a in obj['activityFlow'].iteritems():
            p_id = self.get_plan_id(a_id)
            entity[p_id] = {'prov:id': '%s' % p_id, 'prov:label': 'Plan for %s' % a.name, 'prov:type': 'prov:Plan'}
        return entity

    def get_agent(self, obj):
        agent = {}
        for a_id, a in obj['agent'].iteritems():
            data = AgentSerializer(a).data
            agent[a_id] = data

        return agent

    def get_used(self, obj):
        used = {}
        for u_id, u in obj['used'].iteritems():
            data = UsedSerializer(u).data
            u_id = self.add_relationnamespace(u_id)
            used[u_id] = self.restructure_relations(data)

        return used

    def get_wasGeneratedBy(self, obj):
        wasGeneratedBy = {}
        for w_id, w in obj['wasGeneratedBy'].iteritems():
            data = WasGeneratedBySerializer(w).data
            w_id = self.add_relationnamespace(w_id)
            wasGeneratedBy[w_id] = self.restructure_relations(data)

        return wasGeneratedBy

    def get_wasAssociatedWith(self, obj):
        wasAssociatedWith = {}
        for w_id, w in obj['wasAssociatedWith'].iteritems():
            data = WasAssociatedWithSerializer(w).data
            w_id = self.add_relationnamespace(w_id)
            wasAssociatedWith[w_id] = self.restructure_relations(data)

        # link activities of an activityFlow with its plan
        result = WasAssociatedWith.objects.aggregate(Max('id'))
        i = int(result['id__max'])

        for hs_id, hs in obj['hadStep'].iteritems():
            p_id = self.get_plan_id(hs.activityFlow.id)
            w_id = self.add_relationnamespace(i)
            wasAssociatedWith[w_id] = {'prov:activity': hs.activity.id, 'prov:plan': p_id, 'voprov:votype': 'hadStep'}
            i += 1

        # link plan with activityFlow itself
        for a_id, a in obj['activityFlow'].iteritems():
            p_id = self.get_plan_id(a_id)
            w_id = self.add_relationnamespace(i)
            wasAssociatedWith[w_id] = {'prov:activity': a_id, 'prov:plan': p_id, 'voprov:votype': 'hadStep'}
            i += 1

        return wasAssociatedWith

    def get_wasAttributedTo(self, obj):
        wasAttributedTo = {}
        for w_id, w in obj['wasAttributedTo'].iteritems():
            data = WasAttributedToSerializer(w).data
            w_id = self.add_relationnamespace(w_id)
            wasAttributedTo[w_id] = self.restructure_relations(data)

        return wasAttributedTo

    def get_hadMember(self, obj):
        hadMember = {}
        for h_id, h in obj['hadMember'].iteritems():
            data = HadMemberSerializer(h).data
            h_id = self.add_relationnamespace(h_id)
            hadMember[h_id] = self.restructure_relations(data)

        return hadMember

    def get_wasDerivedFrom(self, obj):
        wasDerivedFrom = {}
        for w_id, w in obj['wasDerivedFrom'].iteritems():
            data = WasDerivedFromSerializer(w).data
            w_id = self.add_relationnamespace(w_id)
            wasDerivedFrom[w_id] = self.restructure_relations(data)

        return wasDerivedFrom

    def get_wasInformedBy(self, obj):
        wasInformedBy = {}
        for w_id, w in obj['wasInformedBy'].iteritems():
            data = WasInformedBySerializer(w).data
            w_id = self.add_relationnamespace(w_id)
            wasInformedBy[w_id] = self.restructure_relations(data)

        return wasInformedBy


    def restructure_qualifiers(self, data):
        # Restructure serialisation of qualified values

        # exclude id in serialisation
        # (since it is used as key for this class instance anyway)
        data.pop('id')

        for key, value in data.iteritems():
            # restructure serialisation of qualified values
            if ':' in value:
                # need to split up, specify that qualified string is used
                val = {}
                val['$'] = value
                val['type'] = "xsd:QName"
                data[key] = val

        # This can actually also be used for integers (xsd:integer), xsd:anyUri etc.
        # Not used here for now.

        return data

    def add_relationnamespace(self, objectId):
        # Add blank namespace '_' to relation ids, if there is no namespace yet,
        # because in W3C ids must be qualified strings; will be needed for json format
        ns = "_"
        if ":" not in str(objectId):
            objectId = ns + ":" + str(objectId)
        return objectId

    def restructure_relations(self, data):
        # Takes a dictionary from a relation serialization,
        # adds "prov" namespace to the fields,
        # because this is required by the prov-library.
        # Do NOT split up qualified foreign key values.
        # Returns the modified dictionary.
        # TODO: Find a more elegant solution for this!

        # exclude id in serialisation of relations
        # (since it is used as key for this class instance anyway)
        data.pop('id')

        for key, value in data.iteritems():

            # replace prov_ by prov for the given keys:
            if key in ['id', 'activity', 'entity', 'collection', 'agent', 'generatedEntity', 'usedEntity', 'usage', 'generation', 'role', 'informed', 'informant']:
                newkey = 'prov:' + key
                data[newkey] = data.pop(key)

        return data

    def get_plan_id(self, a_id):
        p_id = "%s_plan" % a_id
        return p_id


# IVOA specific serializers
class VOActivitySerializer(NonNullCustomSerializer):

    voprov_id = CustomCharField(source='id', custom_field_name='voprov:id')
    voprov_name = CustomCharField(source='name', custom_field_name='voprov:name')
    voprov_type = CustomCharField(source='type', custom_field_name='voprov:type')
    voprov_annotation = CustomCharField(source='annotation', custom_field_name='voprov:annotation')
    voprov_startTime = CustomDateTimeField(source='startTime', custom_field_name='voprov:startTime')
    voprov_endTime = CustomDateTimeField(source='endTime', custom_field_name='voprov:endTime')
    voprov_doculink = CustomCharField(source='doculink', custom_field_name='voprov:doculink')

    class Meta:
        model = Activity
        fields = ('voprov_id', 'voprov_name', 'voprov_type', 'voprov_annotation', 'voprov_startTime', 'voprov_endTime', 'voprov_doculink')


class VOActivityFlowSerializer(VOActivitySerializer):

    class Meta:
        model = ActivityFlow
        fields = ('voprov_id', 'voprov_name', 'voprov_type', 'voprov_annotation', 'voprov_startTime', 'voprov_endTime', 'voprov_doculink')


class VOEntitySerializer(NonNullCustomSerializer):

    voprov_id = CustomCharField(source='id', custom_field_name='voprov:id')
    voprov_name = CustomCharField(source='name', custom_field_name='voprov:name')
    voprov_type = CustomCharField(source='type', custom_field_name='voprov:type')
    voprov_annotation = CustomCharField(source='annotation', custom_field_name='voprov:annotation')
    voprov_rights = CustomCharField(source='rights', custom_field_name='voprov:rights')
    voprov_dataType = CustomCharField(source='dataType', custom_field_name='voprov:dataType')
    voprov_storageLocation = CustomCharField(source='storageLocation', custom_field_name='voprov:storageLocation')

    class Meta:
        model = Entity
        fields = ('voprov_id', 'voprov_name', 'voprov_type', 'voprov_annotation', 'voprov_rights', 'voprov_dataType', 'voprov_storageLocation')


class VOCollectionSerializer(VOEntitySerializer):

    class Meta:
        model = Collection
        fields = ('voprov_id', 'voprov_name', 'voprov_type', 'voprov_annotation', 'voprov_rights', 'voprov_dataType', 'voprov_storageLocation')


class VOAgentSerializer(NonNullCustomSerializer):

    voprov_id = CustomCharField(source='id', custom_field_name='voprov:id')
    voprov_type = CustomCharField(source='type', custom_field_name='voprov:type')
    voprov_name = CustomCharField(source='name', custom_field_name='voprov:name')
    voprov_email = CustomCharField(source='email', custom_field_name='voprov:email')
    voprov_annotation = CustomCharField(source='annotation', custom_field_name='voprov:annotation')

    class Meta:
        model = Agent
        fields = ('voprov_id', 'voprov_name', 'voprov_type', 'voprov_email', 'voprov_annotation')


class VOUsedSerializer(NonNullCustomSerializer):

    class Meta:
        model = Used
        fields = '__all__'


class VOWasGeneratedBySerializer(NonNullCustomSerializer):

    class Meta:
        model = WasGeneratedBy
        fields = '__all__'


class VOWasAssociatedWithSerializer(NonNullCustomSerializer):

    class Meta:
        model = WasAssociatedWith
        fields = '__all__'


class VOWasAttributedToSerializer(NonNullCustomSerializer):

    class Meta:
        model = WasAttributedTo
        fields = '__all__'


class VOHadMemberSerializer(NonNullCustomSerializer):

    class Meta:
        model = HadMember
        fields = '__all__'


class VOWasDerivedFromSerializer(NonNullCustomSerializer):

    class Meta:
        model = WasDerivedFrom
        fields = '__all__'

class VOHadStepSerializer(NonNullCustomSerializer):

    class Meta:
        model = HadStep
        fields = '__all__'


class VOWasInformedBySerializer(NonNullCustomSerializer):

    class Meta:
        model = WasInformedBy
        fields = '__all__'


class VOProvenanceSerializer(serializers.Serializer):

    activity = serializers.SerializerMethodField()
    entity = serializers.SerializerMethodField()
    collection = serializers.SerializerMethodField()
    agent = serializers.SerializerMethodField()
    used = serializers.SerializerMethodField()
    wasGeneratedBy = serializers.SerializerMethodField()
    wasAssociatedWith = serializers.SerializerMethodField()
    wasAttributedTo = serializers.SerializerMethodField()
    hadMember = serializers.SerializerMethodField()
    wasDerivedFrom = serializers.SerializerMethodField()
    wasInformedBy = serializers.SerializerMethodField()
    hadStep = serializers.SerializerMethodField()
    activityFlow = serializers.SerializerMethodField()
    prefix = serializers.SerializerMethodField()

    def get_prefix(self, obj):
        return obj['prefix']

    # get all the class instances serialized by their
    # corresponding serializer;
    # adjust the serialization, where necessary, for each item
    def get_activity(self, obj):
        activity = {}
        for a_id, a in obj['activity'].iteritems():
            data = VOActivitySerializer(a).data
            activity[a_id] = data

        return activity

    def get_activityFlow(self, obj):
        activityFlow = {}
        for a_id, a in obj['activityFlow'].iteritems():
            data = VOActivityFlowSerializer(a).data
            activityFlow[a_id] = data

        return activityFlow


    def get_entity(self, obj):
        entity = {}
        for e_id, e in obj['entity'].iteritems():
            data = VOEntitySerializer(e).data
            entity[e_id] = data

        return entity

    def get_collection(self, obj):
        collection = {}
        for c_id, c in obj['collection'].iteritems():
            data = VOCollectionSerializer(c).data
            collection[c_id] = data

        return collection

    def get_agent(self, obj):
        agent = {}
        for a_id, a in obj['agent'].iteritems():
            data = VOAgentSerializer(a).data
            agent[a_id] = data

        return agent

    def get_used(self, obj):
        used = {}
        for u_id, u in obj['used'].iteritems():
            data = VOUsedSerializer(u).data
            u_id = self.add_relationnamespace(u_id)
            used[u_id] = self.restructure_relations(data)

        return used

    def get_wasGeneratedBy(self, obj):
        wasGeneratedBy = {}
        for w_id, w in obj['wasGeneratedBy'].iteritems():
            data = VOWasGeneratedBySerializer(w).data
            w_id = self.add_relationnamespace(w_id)
            wasGeneratedBy[w_id] = self.restructure_relations(data)

        return wasGeneratedBy

    def get_wasAssociatedWith(self, obj):
        wasAssociatedWith = {}
        for w_id, w in obj['wasAssociatedWith'].iteritems():
            data = VOWasAssociatedWithSerializer(w).data
            w_id = self.add_relationnamespace(w_id)
            wasAssociatedWith[w_id] = self.restructure_relations(data)

        return wasAssociatedWith

    def get_wasAttributedTo(self, obj):
        wasAttributedTo = {}
        for w_id, w in obj['wasAttributedTo'].iteritems():
            data = VOWasAttributedToSerializer(w).data
            w_id = self.add_relationnamespace(w_id)
            wasAttributedTo[w_id] = self.restructure_relations(data)

        return wasAttributedTo

    def get_hadMember(self, obj):
        hadMember = {}
        for h_id, h in obj['hadMember'].iteritems():
            data = VOHadMemberSerializer(h).data
            h_id = self.add_relationnamespace(h_id)
            hadMember[h_id] = self.restructure_relations(data)

        return hadMember

    def get_wasDerivedFrom(self, obj):
        wasDerivedFrom = {}
        for w_id, w in obj['wasDerivedFrom'].iteritems():
            data = VOWasDerivedFromSerializer(w).data
            w_id = self.add_relationnamespace(w_id)
            wasDerivedFrom[w_id] = self.restructure_relations(data)

        return wasDerivedFrom

    def get_hadStep(self, obj):
        hadStep = {}
        for h_id, h in obj['hadStep'].iteritems():
            data = VOHadStepSerializer(h).data
            h_id = self.add_relationnamespace(h_id)
            hadStep[h_id] = self.restructure_relations(data)

        return hadStep

    def get_wasInformedBy(self, obj):
        wasInformedBy = {}
        for w_id, w in obj['wasInformedBy'].iteritems():
            data = VOWasInformedBySerializer(w).data
            w_id = self.add_relationnamespace(w_id)
            wasInformedBy[w_id] = self.restructure_relations(data)

        return wasInformedBy

    def add_relationnamespace(self, objectId):
        # If there is no namespace yet, add the default namespace instead
        ns = "_"
        if ":" not in str(objectId):
            objectId = ns + ":" + str(objectId)
        return objectId

    def restructure_relations(self, data):
        # Takes a dictionary from a relation serialization,
        # adds "prov" namespace to the fields,
        # because this is required by the prov-library.
        # Do NOT split up qualified foreign key values.
        # Returns the modified dictionary.
        # TODO: Find a more elegant solution for this!

        # exclude id in serialisation of relations
        # (since it is used as key for this class instance anyway)
        data.pop('id')

        for key, value in data.iteritems():

            # replace prov_ by prov for the given keys:
            if key in ['activity', 'activityFlow', 'entity', 'collection', 'agent', 'generatedEntity', 'usedEntity', 'usage', 'generation', 'role', 'informed', 'informant']:
                newkey = 'voprov:' + key
                data[newkey] = data.pop(key)

        return data


class ProvenanceGraphSerializer(serializers.Serializer):
    # Restructure an already serialized prov-dataset (dictionary),
    # for usage with d3.js library or similar,
    # for graphical representation of the provenance record
    _model = ""

    nodes = serializers.SerializerMethodField()
    links = serializers.SerializerMethodField()

    _map_nodes_ids = {}    # maps ids of nodes to integers, for use in links-list

    def __init__(self, obj, model="IVOA"):
        serializers.Serializer.__init__(self, obj)
        self._model = model


    def get_nodes(self, obj):
        print 'nodes model: ', self._model
        if self._model == 'IVOA':
            name = 'voprov:name'
            nid = 'voprov:id'
        elif self._model == 'W3C':
            name = 'prov:label'
            nid = 'prov:id'
        else:
            name = 'id'
            nid = 'id'

        nodes = []
        count_nodes = 0
        map_nodes_ids = {}

        # nodes
        for key in ['activity', 'entity', 'agent', 'activityFlow', 'collection']:
            if key in obj:
                for n_id, n in obj[key].iteritems():
                    nodes.append({'name': n[name], 'type': key})
                    map_nodes_ids[n[nid]] = count_nodes
                    count_nodes += 1
        self._map_nodes_ids = map_nodes_ids
        return nodes

    def get_links(self, obj):
        # relations

        if self._model == 'IVOA':
            ns = 'voprov'
        elif self._model == 'W3C':
            ns = 'prov'
        else:
            ns = '_'

        map_nodes_ids = self._map_nodes_ids
        links = []
        count_links = 0

        if 'used' in obj:
            for r_id, r in obj['used'].iteritems():
                value = 0.5
                links.append({
                    'source': map_nodes_ids[r[self.add_namespace('activity', ns)]],
                    'target': map_nodes_ids[r[self.add_namespace('entity', ns)]],
                    'value': value,
                    'type': 'used'
                })
                count_links += 1

        if 'wasGeneratedBy' in obj:
            for r_id, r in obj['wasGeneratedBy'].iteritems():
                value = 0.5
                links.append({
                    'source': map_nodes_ids[r[self.add_namespace('entity', ns)]],
                    'target': map_nodes_ids[r[self.add_namespace('activity', ns)]],
                    'value': value,
                    'type': 'wasGeneratedBy'
                })
                count_links += 1

        if 'wasAssociatedWith' in obj:
            for r_id, r in obj['wasAssociatedWith'].iteritems():
                print r
            for r_id, r in obj['wasAssociatedWith'].iteritems():
                value = 0.2
                # if there is an agent, link to it:
                if self.add_namespace('agent', ns) in r:
                    links.append({
                        'source': map_nodes_ids[r[self.add_namespace('agent', ns)]],
                        'target': map_nodes_ids[r[self.add_namespace('activity', ns)]],
                        'value': value,
                        'type': 'wasAssociatedWith'
                    })
                    count_links += 1
                # if there is a plan, also link to it:
                if self.add_namespace('plan', ns) in r:
                    links.append({
                        'source': map_nodes_ids[r[self.add_namespace('plan', ns)]],
                        'target': map_nodes_ids[r[self.add_namespace('activity', ns)]],
                        'value': value,
                        'type': 'wasAssociatedWith'
                    })
                    count_links += 1

        if 'wasAttributedTo' in obj:
            for r_id, r in obj['wasAttributedTo'].iteritems():
                value = 0.2
                links.append({
                    'source': map_nodes_ids[r[self.add_namespace('agent', ns)]],
                    'target': map_nodes_ids[r[self.add_namespace('entity', ns)]],
                    'value': value,
                    'type': 'wasAttributedTo'
                })
                count_links += 1

        if 'hadMember' in obj:
            for r_id, r in obj['hadMember'].iteritems():
                value = 0.2
                links.append({
                    'source': map_nodes_ids[r[self.add_namespace('collection', ns)]],
                    'target': map_nodes_ids[r[self.add_namespace('entity', ns)]],
                    'value': value,
                    'type': 'hadMember'
                })
                count_links += 1

        if 'wasDerivedFrom' in obj:
            for r_id, r in obj['wasDerivedFrom'].iteritems():
                value = 0.2
                links.append({
                    'source': map_nodes_ids[r[self.add_namespace('generatedEntity', ns)]],
                    'target': map_nodes_ids[r[self.add_namespace('usedEntity', ns)]],
                    'value': value,
                    'type': 'wasDerivedFrom'
                })
                count_links += 1

        if 'hadStep' in obj:
            for r_id, r in obj['hadStep'].iteritems():
                value = 0.2
                links.append({
                    'source': map_nodes_ids[r[self.add_namespace('activityFlow', ns)]],
                    'target': map_nodes_ids[r[self.add_namespace('activity', ns)]],
                    'value': value,
                    'type': 'hadStep'
                })
                count_links += 1

        if 'wasInformedBy' in obj:
            for r_id, r in obj['wasInformedBy'].iteritems():
                value = 0.2
                links.append({
                    'source': map_nodes_ids[r[self.add_namespace('informed', ns)]],
                    'target': map_nodes_ids[r[self.add_namespace('informant', ns)]],
                    'value': value,
                    'type': 'wasInformedBy'
                })
                count_links += 1

        return links

    def add_namespace(self, value, namespace):
        ns_value = "%s:%s" % (namespace, value)
        return ns_value