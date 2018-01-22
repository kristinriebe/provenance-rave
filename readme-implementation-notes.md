Implementation notes
====================

The Django web application framework provides a convenient way to implement the provenance classes directly as Django models. The definition of these classes along with general views and forms for retrieving data stored within the corresponding database are now moved into a separate, reusable app [django-prov_vo](https://github.com/kristinriebe/django-prov_vo) (the suffix `_vo` is used to stress that it's the provenance data model of the virtual observatory).The implementation notes concerning the implementation of this part have been moved to [https://github.com/kristinriebe/django-prov_vo/readme-implementation-notes.md].

Provenance classes can be implemented directly as Django model classes.
When using Django RestFramework, one can easily get an API for retrieving
all activities/entities etc., getting details for one of them etc.

Updating an object or adding a new one via the REST API is not implemented.

## TODO:
* Load more 'real' data
* Use description-classes
* Move VOSI-endpoints to prov_vo