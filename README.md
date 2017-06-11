# Provenance webapp for RAVE using Django
This webapp is used as a testing environment for implementing the current IVOA Provenance Data Model/W3C model.

**Warning: This is at a very preliminary state, used only for testing purposes and object to many changes! No guarantees for anything!**


## Dependencies/Installation
Install Django  

```shell
pip install django
```

and following packages (use `pip install <package>`):

* django-braces        # for json views
* djangorestframework  # rest
* django-extensions    # e.g. for exporting model graphs
* django-test-without-migrations  # for enabling tests of unmanaged models
* pygments
* markdown
* BeautifulSoup         # xml parsing

Install graphviz package additionally for model graphs:

```
apt-get install libgraphviz-dev
pip install pygraphviz
```


## Starting the webapp
When everything is installed, start django's test server in the usual way:

```
python manage.py runserver
```

and point a web browser to `localhost:8000`. Note that you can also provide a different port as additional argument to manage.py and point your web browser to the other port.

The webapp should be visible in the browser and it should even work offline, since all libraries are stored in the directory: `provenance-rave/provapp/static`.


## Running tests
Run tests using:

```shell
python manage.py test --nomigrations --settings=provsite.test_settings
```

This will load the additional settings from the test_settings-file and the
option `--nomigrations` is used for avoiding the need of migrations when just
testing the model.


## Get a model graph
```shell
python manage.py graph_models provapp -o test.png
```

This produces a file `test.png` for all models from provapp.
This requires that the graphviz library is installed additionally, see above.


## Features
This webapp allows to:

* Retrieve information on activities, entities or agents from the database (list/detail view, using REST api)
* Display a graphical representation of the (full) provenance graph (sankey, force-directed graph)
* Get a PROVN-representation of the (full) provenance information (main path, using collections)
* Get detailed (no collections) or basic (only collections) provenance graphs for a given `RAVE_OBS_ID` (but there are just 2 `RAVE_OBS_ID` included in data right now).
* Prov-DAL endpoint: 
    - Get provenance record in PROV-JSON or PROV-N format for any given entity id
    - specify ID, STEP, FORMAT and also MODEL (IVOA or W3C) for serializations
    - also allows multiple (entity) ids, e.g. via:
      `http://localhost:8002/provapp/provdal/?ID=vo:UCAC4&ID=rave:20121220_0752m383I00009_fits&STEP=ALL&FORMAT=PROV-N&MODEL=W3C`
    - additionally provides option to display retrieved data as interactive
      graphical representation using javascript (d3.js)

* Uses Django REST Framework for automatic list and detail views
* Uses serializers for different model serialization (W3C/IVOA)
* Use renderer for PROV-N


## TODO:
* Proper error handling
* Write tests for checking all the functionality
* Use MySQL database/remote database instead of Sqlite3

* Implement xml serialization, votable serialization
* Clean up, remove unnecessary parts
* Use prov-json and provjs from W3C model and Southhamption Provenance tools instead of custom made json and javascript (?)
* Use functions for detailed views, instead of loading everything into database?

* Implement ActivityFlow
* Implement Description side
* Connect with real data from the real RAVE database
* Write implementation report, including nice overview on used classes (graphical?), also see readme-implementation-notes.txt


