from collections import OrderedDict

from rest_framework import serializers
from rest_framework.fields import SkipField, empty
from rest_framework.relations import PKOnlyObject

from .models import (
    Activity,
    Entity,
    Agent,
    Used,
    WasGeneratedBy,
    WasAssociatedWith,
    WasAttributedTo,
    HadMember,
    WasDerivedFrom
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


# IVOA specific serializer
class ActivitySerializerVO(NonNullCustomSerializer):

    class Meta:
        model = Activity
        fields = ('id', 'name', 'type', 'description')


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
    voprov_name = CustomCharField(source='name', custom_field_name='voprov:name')
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

    class Meta:
        model = WasAttributedTo
        fields = '__all__'


class HadMemberSerializer(NonNullCustomSerializer):

    class Meta:
        model = HadMember
        fields = '__all__'


class WasDerivedFromSerializer(NonNullCustomSerializer):

    class Meta:
        model = WasDerivedFrom
        fields = '__all__'


class ProvenanceSerializer(serializers.Serializer):

    # prefix = {}

    activity = serializers.SerializerMethodField()
    entity = serializers.SerializerMethodField()
    agent = serializers.SerializerMethodField()
    used = serializers.SerializerMethodField()
    wasGeneratedBy = serializers.SerializerMethodField()
    wasAssociatedWith = serializers.SerializerMethodField()
    wasAttributedTo = serializers.SerializerMethodField()
    hadMember = serializers.SerializerMethodField()
    wasDerivedFrom = serializers.SerializerMethodField()

    # get all the class instances serialized by their
    # corresponding serializer;
    # adjust the serialization, where necessary, for each item

    def get_activity(self, obj):
        activity = {}
        for a_id, a in obj['activity'].iteritems():
            data = ActivitySerializer(a).data
            activity[a_id] = data #self.restructure_qualifiers(data)

        return activity

    def get_entity(self, obj):
        entity = {}
        for e_id, e in obj['entity'].iteritems():
            data = EntitySerializer(e).data
            entity[e_id] = (data)

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
            used[u_id] = self.restructure_relationqualifiers(data)

        return used

    def get_wasGeneratedBy(self, obj):
        wasGeneratedBy = {}
        for w_id, w in obj['wasGeneratedBy'].iteritems():
            data = WasGeneratedBySerializer(w).data
            w_id = self.add_relationnamespace(w_id)
            wasGeneratedBy[w_id] = self.restructure_relationqualifiers(data)

        return wasGeneratedBy

    def get_wasAssociatedWith(self, obj):
        wasAssociatedWith = {}
        for w_id, w in obj['wasAssociatedWith'].iteritems():
            data = WasAssociatedWithSerializer(w).data
            w_id = self.add_relationnamespace(w_id)
            wasAssociatedWith[w_id] = self.restructure_relationqualifiers(data)

        return wasAssociatedWith

    def get_wasAttributedTo(self, obj):
        wasAttributedTo = {}
        for w_id, w in obj['wasAttributedTo'].iteritems():
            data = WasAttributedToSerializer(w).data
            w_id = self.add_relationnamespace(w_id)
            wasAttributedTo[w_id] = self.restructure_relationqualifiers(data)

        return wasAttributedTo

    def get_hadMember(self, obj):
        hadMember = {}
        for h_id, h in obj['hadMember'].iteritems():
            data = HadMemberSerializer(h).data
            h_id = self.add_relationnamespace(h_id)
            hadMember[h_id] = self.restructure_relationqualifiers(data)

        return hadMember

    def get_wasDerivedFrom(self, obj):
        wasDerivedFrom = {}
        for w_id, w in obj['wasDerivedFrom'].iteritems():
            data = WasDerivedFromSerializer(w).data
            w_id = self.add_relationnamespace(w_id)
            wasDerivedFrom[w_id] = self.restructure_relationqualifiers(data)

        return wasDerivedFrom


    def restructure_qualifiers(self, data):
        # Takes a dictionary, replaces prov_ by prov: and
        # adds type to qualified values
        # Returns the modified dictionary
        # TODO: Find a more elegant solution for this!

        # exclude id in serialisation
        # (since it is used as key for this class instance anyway)
        data.pop('id')

        for key, value in data.iteritems():

            # replace prov_ by prov: -- done directly in to_represenation now, using custom_field_name
            # could also just add the qualifier here just for specific keywords

            # restructure serialisation of qualified values
            if ':' in value:
                # need to split up, specify that qualified string is used
                val = {}
                val['$'] = value
                val['type'] = "xsd:QName"
                data[key] = val

        return data

    def add_relationnamespace(self, objectId):
        ns = "_"
        if ":" not in str(objectId):
            objectId = ns + ":" + str(objectId)
        return objectId

    def restructure_relationqualifiers(self, data):
        # Takes a dictionary from a relation serialization,
        # adds "prov" namespace to the foreign key fields,
        # because this is required by the prov-library.
        # Do NOT split up qualified foreign key values.
        # Returns the modified dictionary.
        # TODO: Find a more elegant solution for this!

        # exclude id in serialisation
        # (since it is used as key for this class instance anyway)
        data.pop('id')

        for key, value in data.iteritems():

            # replace prov_ by prov:
            # TODO: how to check, if it is a foreign key or an additional attribute??
            # For now, just put "prov:" everywhere
            if key in ['id', 'activity', 'entity', 'collection', 'agent','generatedEntity', 'usedEntity', 'usage', 'generation', 'role']:
                newkey = 'prov:'+ key
                data[newkey] = data.pop(key)

            # restructure serialisation of qualified values -- not needed here.

        return data