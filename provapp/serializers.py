from rest_framework import serializers

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


class ActivitySerializer(serializers.ModelSerializer):

    prov_type = serializers.CharField(source='type')
    prov_label = serializers.CharField(source='name')
    prov_description = serializers.CharField(source='annotation')

    class Meta:
        model = Activity
        fields = ('id', 'prov_label', 'prov_type', 'prov_description')
        # exclude id later on, when it will be used as key in the dictionary anyway
        # but still keep it here in the serializer


class EntitySerializer(serializers.ModelSerializer):

    prov_type = serializers.CharField(source='type')
    prov_label = serializers.CharField(source='name')
    prov_description = serializers.CharField(source='annotation')
    #prov_type = serializers.SerializerMethodField() #field_name = "prov:type")
    # But this is now readonly, i.e. could not be filled when using rest api for creating new entity or updating!

    class Meta:
        model = Entity
        fields = ('id', 'prov_label', 'prov_type', 'prov_description')


class AgentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Agent
        fields = '__all__'


class UsedSerializer(serializers.ModelSerializer):

    class Meta:
        model = Used
        fields = '__all__'


class WasGeneratedBySerializer(serializers.ModelSerializer):

    class Meta:
        model = WasGeneratedBy
        fields = '__all__'


class WasAssociatedWithSerializer(serializers.ModelSerializer):

    class Meta:
        model = WasAssociatedWith
        fields = '__all__'


class WasAttributedToSerializer(serializers.ModelSerializer):

    class Meta:
        model = WasAttributedTo
        fields = '__all__'


class HadMemberSerializer(serializers.ModelSerializer):

    class Meta:
        model = HadMember
        fields = '__all__'


class WasDerivedFromSerializer(serializers.ModelSerializer):

    class Meta:
        model = WasDerivedFrom
        fields = '__all__'



class ProvenanceSerializer(serializers.Serializer):

    activity = serializers.SerializerMethodField()
    entity = serializers.SerializerMethodField()
    agent = serializers.SerializerMethodField()
    used = serializers.SerializerMethodField()
    wasDerivedFrom = serializers.SerializerMethodField()
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
            activity[a_id] = self.restructure_qualifiers(data)

        return activity

    def get_entity(self, obj):
        entity = {}
        for e_id, e in obj['entity'].iteritems():
            data = EntitySerializer(e).data
            entity[e_id] = self.restructure_qualifiers(data)

        return entity

    def get_agent(self, obj):
        agent = {}
        for a_id, a in obj['agent'].iteritems():
            data = AgentSerializer(a).data
            agent[a_id] = self.restructure_qualifiers(data)

        return agent

    def get_used(self, obj):
        used = {}
        for u_id, u in obj['used'].iteritems():
            data = UsedSerializer(u).data
            used[u_id] = self.restructure_qualifiers(data)

        return used

    def get_wasGeneratedBy(self, obj):
        wasGeneratedBy = {}
        for w_id, w in obj['wasGeneratedBy'].iteritems():
            data = WasGeneratedBySerializer(w).data
            wasGeneratedBy[w_id] = self.restructure_qualifiers(data)

        return wasGeneratedBy

    def get_wasAssociatedWith(self, obj):
        wasAssociatedWith = {}
        for w_id, w in obj['wasAssociatedWith'].iteritems():
            data = WasAssociatedWithSerializer(w).data
            wasAssociatedWith[w_id] = self.restructure_qualifiers(data)

        return wasAssociatedWith

    def get_wasAttributedTo(self, obj):
        wasAttributedTo = {}
        for w_id, w in obj['wasAttributedTo'].iteritems():
            data = WasAttributedToSerializer(w).data
            wasAttributedTo[w_id] = self.restructure_qualifiers(data)

        return wasAttributedTo

    def get_hadMember(self, obj):
        hadMember = {}
        for h_id, h in obj['hadMember'].iteritems():
            data = HadMemberSerializer(h).data
            hadMember[h_id] = self.restructure_qualifiers(data)

        return hadMember

    def get_wasDerivedFrom(self, obj):
        wasDerivedFrom = {}
        for w_id, w in obj['wasDerivedFrom'].iteritems():
            data = WasDerivedFromSerializer(w).data
            wasDerivedFrom[w_id] = self.restructure_qualifiers(data)

        return wasDerivedFrom


    def restructure_qualifiers(self, data):
        # Takes a dictionary, replaces prov_ by prov: and
        # adds type to qualified values
        # Returns the modified dictionary

        # exclude id in serialisation
        # (since it is used as key for this class instance anyway)
        data.pop('id')

        for key, value in data.iteritems():

            # replace prov_by prov:
            if key.startswith('prov_'):
                newkey = key.replace('prov_', 'prov:')
                data[newkey] = data.pop(key)

            # restructure serialisation of qualified values
            if ':' in value:
                # need to split up, specify that qualified string is used
                val = {}
                val['$'] = value
                val['type'] = "xsd:QName"
                data[key] = val

        return data