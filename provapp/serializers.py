from rest_framework import serializers

from .models import (
    Activity,
    Entity,
    Agent,
    Used,
    WasGeneratedBy,
    HadMember,
    WasDerivedFrom,
    WasAssociatedWith,
    WasAttributedTo
    )


class ActivitySerializer(serializers.ModelSerializer):

    class Meta:
        model = Activity
        fields = ('id', 'name', 'type', 'annotation')


class EntitySerializer(serializers.ModelSerializer):

    prov_type = serializers.CharField(source='type')
    prov_label = serializers.CharField(source='name')
    prov_description = serializers.CharField(source='annotation')
    #prov_type = serializers.SerializerMethodField() #field_name = "prov:type")
    # But this is now readonly, i.e. could not be filled when using rest api for creating new entity or updating!


    class Meta:
        model = Entity
        fields = ('id', 'prov_label', 'prov_type', 'prov_description')

    #def get_prov_type(self, obj):
    #    value = obj.type
#
#        valuearr = obj.type.split(':')
#        if len(valuearr) == 2:
#            value = {}
#            value['$'] = obj.type
#            value['type'] = "xsd:QName" # or prov:QUALIFIED_NAME as used in Prov_Store
#
#        return value


class AgentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Agent
        fields = '__all__'


class ProvenanceSerializer(serializers.Serializer):

    activity = serializers.SerializerMethodField()
    entity = serializers.SerializerMethodField()
    agent = serializers.SerializerMethodField()


    # get all the class instances serialized by their
    # corresponding serializer;
    # adjust the serialization, where necessary

    def get_activity(self, obj):
        activity = {}
        for a_id, a in obj['activity'].iteritems():
            serializer = ActivitySerializer(a)
            data = serializer.data

            for key, value in data.iteritems():

                # replace prov_by prov:
                if key.startswith('prov_'):
                    newkey = key.replace('prov_', 'prov:')
                    data[newkey] = data.pop[key]

                # restructure serialisation of qualified values
                if ':' in value:
                    # need to split up, specify that qualified string is used
                    val = {}
                    val['$'] = value
                    val['type'] = "xsd:QName"
                    data[key] = val

            activity[a_id] = data

        return activity

    def get_entity(self, obj):
        entity = {}
        for e_id, e in obj['entity'].iteritems():
            serializer = EntitySerializer(e)
            data = serializer.data

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

            entity[e_id] = data

            # while doing this, add qualifier to keys, where needed
            #entity[e_id]['prov:type'] = entity[e_id].pop('type')
            #if 'label' in entity[e_id]:
            #    entity[e_id]['prov:label'] = entity[e_id].pop('label')
        return entity

    def get_agent(self, obj):
        agent = {}
        for a_id, a in obj['agent'].iteritems():
            agent[a_id] = AgentSerializer(a).data
        return agent
