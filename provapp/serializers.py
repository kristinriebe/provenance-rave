from rest_framework import serializers

from .models import Activity, Entity, Agent, Used, WasGeneratedBy, HadMember, WasDerivedFrom, WasAssociatedWith, WasAttributedTo


class ActivitySerializer(serializers.ModelSerializer):

    class Meta:
        model = Activity
        fields = ('id', 'label', 'type', 'description')


class EntitySerializer(serializers.ModelSerializer):

    name = serializers.CharField(source='label')
    prov_type = serializers.SerializerMethodField()
    foo = serializers.SerializerMethodField()

    #activity = ActivitySerializer(many=True)

    class Meta:
        model = Entity
        fields = '__all__'
        #fields = ('id', 'label', 'description', 'dataType', 'name', 'foo', 'type')

    def get_foo(self, obj):
        return obj.label + '-hallo'

    def get_prov_type(self, obj):
        value = obj.type

        valuearr = obj.type.split(':')
        if len(valuearr) == 2:
            value = {}
            value['$'] = obj.type
            value['type'] = "xsd:QName" # or prov:QUALIFIED_NAME as used in Prov_Store

        return value


class ProvenanceSerializer(serializers.Serializer):
    activity = serializers.SerializerMethodField()
    entity = serializers.SerializerMethodField()


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
        return entity

    #entity = EntitySerializer(e)
#    data = {'entity': {}, 'activity': {}}

    # # convert querysets to serialized python objects
    # for e_id, e in prov['entity'].iteritems():
    #     serializer = EntitySerializer(e)
    #     data['entity'][e_id] = serializer.data

    # for a_id, a in prov['activity'].iteritems():
    #     serializer = ActivitySerializer(e)
    #     data['activity'][a_id] = serializer.data

#     name = serializers.CharField(source='label')
#     prov_type = serializers.SerializerMethodField()
#     foo = serializers.SerializerMethodField()

