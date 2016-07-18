# Provenance webapp in Django
This webapp is used as a testing environment for implementing the current IVOA Provenance Data Model/W3C model. 

**Warning: This is at a very preliminary state, used only for testing purpoes and object to many changes! No guarantees for anything!**


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

The webapp should be visible in the browser and it should even work offline, since all libraries are stored in the directory: `provsite/provapp/static`.


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
However, it only works, if the graphviz library is installed additionally, see above.


## Features
This webapp allows to:

* Retrieve information on activities, entities or agents from the database
* Display a graphical representation of the (full) provenance graph (sankey, force-directed graph)
* Get a PROVN-representation of the (full) provenance information (main path, using collections)
* First attempt of having detailed or basic provenance for a given RAVE_OBS_ID works (implemented for just one RAVE_OBS_ID right now).


## TODO:
* Write tests for checking all the functionality (i.e. all the views, BEFORE cleaning up everything)
* Clean up javascript for activity-graph (use same as in observation_id-view)
* Clean up, remove unnecessary parts
* Adjust internal data model to currently discussed data model (attributes!)
* Use prov-json and provjs from W3C model and Southhamption Provenance tools instead of custom made json and javascript
* Use functions for detailed views, instead of loading everything into database?
* Use MySQL database/remote database instead of Sqlite3
* Use migrations and fixtures for properly dealing with database
* ...
