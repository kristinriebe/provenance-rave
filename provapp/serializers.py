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

#     name = serializers.CharField(source='label')
    type = serializers.SerializerMethodField() #field_name = "prov:type")
    # But this is now readonly, i.e. could not be filled when using rest api for creating new entity or updating!


    class Meta:
        model = Entity
        fields = ('id', 'name', 'type', 'annotation')

    def get_type(self, obj):
        value = obj.type

        valuearr = obj.type.split(':')
        if len(valuearr) == 2:
            value = {}
            value['$'] = obj.type
            value['type'] = "xsd:QName" # or prov:QUALIFIED_NAME as used in Prov_Store

        return value

#    def to_representation(self, obj):
        #for key, value in obj.items():
        #    print key
        # field_name=...
        # return obj
        #pass
#        return


class AgentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Agent
        fields = '__all__'


class ProvenanceSerializer(serializers.Serializer):
    activity = serializers.SerializerMethodField()
    entity = serializers.SerializerMethodField()
    agent = serializers.SerializerMethodField()


    def get_activity(self, obj):
        activity = {}
        for a_id, a in obj['activity'].iteritems():
            serializer = ActivitySerializer(a)
            activity[a_id] = serializer.data
        return activity

    def get_entity(self, obj):
        entity = {}
        for e_id, e in obj['entity'].iteritems():
            serializer = EntitySerializer(e)
            entity[e_id] = serializer.data

            # while doing this, add qualifier to keys, where needed
            entity[e_id]['prov:type'] = entity[e_id].pop('type')
            if 'label' in entity[e_id]:
                entity[e_id]['prov:label'] = entity[e_id].pop('label')
        return entity

    def get_agent(self, obj):
        agent = {}
        for a_id, a in obj['agent'].iteritems():
            agent[a_id] = AgentSerializer(a).data
        return agent
