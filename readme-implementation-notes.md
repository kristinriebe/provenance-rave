Implementation notes
====================

## General remarks
Provenance classes can be implemented directly as Django model classes.
When using Django RestFramework, one can easily get an API for retrieving
all activities/entities etc., getting details for one of them etc.
Updating an object or adding a new one via the REST API is not tested yet (and will likely fail).

## Tracking provenance
Provenance for an entity or activity can be tracked backwards via the different relations.
Provenance tracking is done recursively, because:
    * It is unknown, how many steps one needs to go backwards.
    * There may be loops, i.e. one node of the provenance graph may be visited multiple times.

I defined two main functions: `find_entity` and `find_activity`.

## Prov-DAL
If a user asks for the provenance record of an entity with option "STEP=LAST", then I interprete it as one step *backwards in time*. I have cases where the backwards provenance of a data item is not recorded, only for the collection to which it belongs. With STEP=LAST I originally returned only 1 provenance relation for the data item, which did not include any "backwards" information (just the hadMember link). Now, in such a case, I track the collection's relations further until at least one wasGeneratedBy or one wasDerivedFrom link is found.

## Implementing Collection
Entities that are collections and can have members are stored as Collection, 
which is an inherited class from Entity. So far, the attributes are not different, thus when serializing/displaying a collection, it has the same attributes as an entity. Also, when loading collection data into the database, collections are stored in the entity-table and only additionally linked from the collection-table. I.e. when looking for an entity or a collection, it's still enough to do the lookup with the entity-table. But if one needs to make sure that something is a collection, then one should look it up in the collection-table.

In W3C serialization, Collections are Entities with type "prov:collection". In IVOA we can serialize them explicitly as collections.
(Having the same attributes as entity + hadMember relationship.)

Advantage of collection as class:
- in HadMember, the collection-attribute must link to a colelction, which is a straight-forward constraint if collection is an extra class
- can check very clearly, if something is a collection or not (even if metadata are incomplete) by checking if the entity occurs in Collection table as well
- if additional attributes are needed, then I need the extra class

Advantage of collection as entity with type 'prov:collection':
- less models (classes) need to be implemented, i.e. also less serializers etc.
- faster, because additional lookup in Colleciton table not needed
    + if I want to know the type, I just look up the attribute type;
    + => no additional database request needed

## Serialization

### Trouble with qualified attributes (prov:type etc.)
The W3C serializations (for PROV-N, PROV-JSON) expect qualified names for attributes, i.e. a namespace must be given for each key, e.g. "prov:label", "prov:type" etc. This is not supported in serializers
from Django RestFramework. I therefore have written a CustomCharField class
that accepts an additional keyword argument `custom_field_name`. Here any
string can be given. This additional attribute is then used by a custom
serializer class (NonNullCustomSerializer) to replace the `field_name`
in the `to_representation` method.

**Idea**: Actually, one could also implement full namespace support and add a "namespace" attribute instead. But the `custom_field_name` implementation
is sufficient for now, especially since I know exactly which namespaces I need
to support.

### Do not serialize null-fields
I have defined a custom basic serializer class, that inherits from ModelSerializer and just overrides the "to_representation"
method. This is the method which converts to the native data object
(an ordered dictionary).

I have implemented 2 important changes:

* skip fields that are not set (Null/None)
* set `field_name` to `custom_field_name` (if exists and not None)


### Blank namespace for identifiers in PROV-N not valid?
When using a blank namespace for relationship ids when rendering PROV-N, the
resulting provn-file cannot be uploaded to ProvStore or ProvValidator (see https://provenance.ecs.soton.ac.uk/validator/view/translator.html). It will fail with

"java.lang.NullPointerException: Namespace.stringToQualifiedName(: Null namespace for _"

Using no namespace is also not allowed, since ids must be qualified names. Therefore I just use namespace "r" for now.


### No explicit datatypes for PROV literals (values)
This is done in PROV-JSON using the construct:

```
"number": {
        "$": "10",
        "type": "xsd:Integer"
}
```

and similar (in PROV-N, the datatypes are marked using %% after the value). The default type is "xsd:string", so if the values are given like this:

```
"number": "10"
```

then a string datatype is assumed. This is good enough for us now, so I'll just skip explicitly mentioning the datatypes for now.

### IVOA serialization
According to the IVOA Provenance DM requirements, is must be possible to serialize the provenance information into at least one of the W3C formats.
Since we also define additional classes and additional/different attributes in IVOA Provenance DM, we also need a serialization format that can reflect these classes and attributes directly.

If someone intends to use provenance records with W3C-clients/tools, he/she should use a W3C compliant serialization. But then one cannot make use of the additional features.
If someone intends to use provenance records with VO-tools, these VO-tools may digest VO-specific information.

Thus, I wrote VO-variants of the serializers for each model, which more directly map the model attributes and use "voprov" as namespace everywhere.

## Issues to be taken care of
* provn serialization needs marker "-" for missing elements, e.g. for time in `used` and `wasGeneratedBy` relationship
* all ids must be qualified (even for relations)
* all attributes must be qualified (even the non-prov attributes)
* `prov:role` is not allowed in wasAttributedTo statements (but it's ok for the others), thus I defined voprov:role for the serialization
* `hadMember` has no id and no optional attributes in W3C (i.e. also no role)

## Validation
use e.g. https://provenance.ecs.soton.ac.uk/validator/view/validator.html
=> works now with my json and provn serialization

https://provenance.ecs.soton.ac.uk/validator/view/translator.html
=> works now as well

Uploading to ProvStore works for rave.json
=> working for json and provn

## TODO
* use description-classes
* use collection class in IVOA ProvenanceDM explicitly!!
* make a difference between graph for W3C/IVOA model!
* find a better solution for providing a dynamic url for graphjson?
* make use of ProvenanceGraphSerializer for overview graph, observationId form etc. as well
* merge find_entity_graph with find_entity etc. to avoid code repetition
* use different api-root for W3C and IVOA (rest framework)
* fix datetime (UTC)
* finish implementing activityFlow:
    - include in javascript (extra color for this; also in force-directed!)
    - auto-generate wasGeneratedBy and used-relationships? Or insert?
        + (but cannot know, which entities are used outside of act. flow and which not! => Have to assume that they all are important.)
    - graphical view: choose viewLevel, show/hide details inside activityFlow

* ProvDAL:
    * Allow to enter an activity id as well

### Soon
* write a general prov-app, with abstract classes; make a new app for each project, derive project-specific classes from abstract classes
    => reusable prov-app as core library

###  At some point later in the future
* maybe use a proper namespace-solution after all?
* add datatypes ($, type) where needed for json and provn serialization




