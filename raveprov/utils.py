from prov_vo.models import (
    Activity, Entity, Agent, Used, WasGeneratedBy,
    WasAssociatedWith, WasAttributedTo, HadMember, WasDerivedFrom,
    WasInformedBy, HadStep, ActivityFlow, Collection
)


# Helper functions for tracking provenance paths
def find_entity_graph(entity, prov, collection="include"):

    # always check membership to collection first (and follow its provenance),
    # no matter if it's a collection or not
    queryset = HadMember.objects.filter(entity=entity.id)
    for h in queryset:
        #print "Entity "+ entity.id + " is member of collection: ", h.collection.id

        # add entity to prov-json, if not yet done
        if h.collection.id not in prov['map_nodes_ids']:
            prov['nodes_dict'].append({'name': h.collection.name, 'type': 'entity'})
            prov['map_nodes_ids'][h.collection.id] = prov['count_nodes']
            prov['count_nodes'] = prov['count_nodes'] + 1

            # follow this collection's provenance (if it was not recorded before)
            prov = find_entity_graph(h.collection, prov, collection=collection)
        else:
            # just find its id:
            id1 = prov['map_nodes_ids'] # not needed, is found below anyway

        # add hadMember-link:
        # but only, if not yet recorded -> how to check?
        prov['links_dict'].append({"source": prov['map_nodes_ids'][h.collection.id], "target": prov['map_nodes_ids'][h.entity.id], "value": 0.2, "type": "hadMember"})
        prov['count_link'] = prov['count_link'] + 1


    # track the provenance information backwards, but possibly only/not for collections!
    if collection == "exclude":
        # return immediately, if it is a collection
        if entity.type == "prov:collection":
            return prov
    elif collection == "only":
        # only continue, if it is a collection, i.e. return if it is not
        if entity.type != "prov:collection":
            return prov
    else:
        # continue, independent of collection type or not
        pass

    queryset = WasGeneratedBy.objects.filter(entity=entity.id)
    for wg in queryset:
        #print "Entity " + entity.id + " wasGeneratedBy activity: ", wg.activity.id

        # add activity to prov-json for graphics, if not yet done
        # (use map_activity_ids for easier checking)

        if wg.activity.id not in prov['map_nodes_ids']:
            prov['nodes_dict'].append({'name': wg.activity.name, 'type': 'activity'})
            prov['map_nodes_ids'][wg.activity.id] = prov['count_nodes']
            prov['count_nodes'] = prov['count_nodes'] + 1

            # follow provenance along this activity
            prov = find_activity_graph(wg.activity, prov, collection=collection)

        # add wasGeneratedBy-link
        prov['links_dict'].append({"source": prov['map_nodes_ids'][wg.entity.id], "target": prov['map_nodes_ids'][wg.activity.id], "value": 0.2, "type": "wasGeneratedBy"})
        prov['count_link'] = prov['count_link'] + 1


    queryset = WasDerivedFrom.objects.filter(generatedEntity=entity.id)
    # this relation is unique, there can be only one ... or not?
    for wd in queryset:
        #print "Entity " + entity.id + " wasDerivedFrom entity ", wd.usedEntity.id

        # add entity to prov-json, if not yet done
        if wd.usedEntity.id not in prov['map_nodes_ids']:
            prov['nodes_dict'].append({'name': wd.usedEntity.name, 'type': 'entity'})
            prov['map_nodes_ids'][wd.usedEntity.id] = prov['count_nodes']
            prov['count_nodes'] = prov['count_nodes'] + 1

            # continue with pre-decessor
            prov = find_entity_graph(wd.usedEntity, prov, collection=collection)

        # add hadMember-link (in any case)
        prov['links_dict'].append({"source": prov['map_nodes_ids'][entity.id], "target": prov['map_nodes_ids'][wd.usedEntity.id], "value": 0.2, "type": "wasDerivedFrom"})
        prov['count_link'] = prov['count_link'] + 1


    # if nothing found until now, then I have reached an endpoint in the graph
    #print "Giving up, no more provenance for entity found."
    return prov


def find_activity_graph(activity, prov, collection="include"):
# basic = only collections; detail = no collections

    # Check used relations
    queryset = Used.objects.filter(activity=activity.id)
    for u in queryset:

        #print "Activity " + activity.id + " used entity ", u.entity.id

        # only continue, if collection or no collection or always
        cont = True
        if collection == "exclude":
            # skip, if it is a collection
            if u.entity.type == "prov:collection":
                cont = False
        elif collection == "only":
            # only continue, if it is a collection, i.e. skip if it is not
            if u.entity.type != "prov:collection":
                cont = False
        else:
            # continue, independent of collection type or not
            pass

        if cont:
            # add entity to prov-json, if not yet done
            if (u.entity.id not in prov['map_nodes_ids']):
                prov['nodes_dict'].append({'name': u.entity.name, 'type': 'entity'})
                prov['map_nodes_ids'][u.entity.id] = prov['count_nodes']
                prov['count_nodes'] = prov['count_nodes'] + 1

                # follow this entity's provenance
                prov = find_entity_graph(u.entity, prov, collection=collection)

            # add used-link:
            prov['links_dict'].append({"source": prov['map_nodes_ids'][activity.id], "target": prov['map_nodes_ids'][u.entity.id], "value": 0.2, "type": "used"})
            prov['count_link'] = prov['count_link'] + 1

    #print "Giving up, no more provenance for activity found."
    return prov

