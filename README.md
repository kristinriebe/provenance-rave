# Provenance webapp for RAVE using Django
This webapp is used as a testing environment for implementing the current IVOA Provenance Data Model, using metadata from the [RAVE](https://www.rave-project.org) project.

A (more or less) live working example is available here (but may be outdated or broken any time):  

https://escience.aip.de/provenance-rave/

**Warning: This is at a very preliminary state, used only for testing purposes and object to many changes! No guarantees for anything!**

## Installation
Clone the git repository:
```
git clone https://github.com/kristinriebe/provenance-rave.git
```

Create a virtual environment and install the required python (2.7) packages:

```
virtualenv -p /usr/bin/python2.7 env
source env/bin/activate

cd provenance-rave
pip install -r requirements.txt
```

The following packages are needed:

django  
djangorestframework  
django-extensions -- for exporting model-graphs
django-test-without-migrations -- for enabling tests of unmanaged models
pygments  
markdown  
BeautifulSoup  
pyyaml  

Install graphviz package additionally, if you want to get images of the used model classes and their attributes (not required for running the web application):

```
apt-get install libgraphviz-dev
pip install pygraphviz
```


## Testing
Run tests using:

```shell
python manage.py test --nomigrations --settings=provenance.test_settings
```

This will load the additional settings from the test_settings-file and the
option `--nomigrations` is used for avoiding the need of migrations when just
testing the model.

Currently, there are only a few tests available, but this will hopefully improve in the future.


## Loading data
Currently, the RAVE metadata can be loaded into the sqlite database with:

```bash
python manage.py loaddata prov_app/fixtures/rave_data.yaml
```

The data can be deleted again using

```bash
cat data/delete_rave_data.sql | sqlite3 db.sqlite3
```

Additionally, observation ids of RAVE are ingested into an additional table `rave_obsids`. Have a look into the `data/` directory to find scripts for loading them directly from a csv file into the database and then post-proccessing the data (using `update_rave_obsids.sql` for adding an id column etc.).

## Starting the webapp locally (test server)
The server settings are read from an extra file `custom_settings.yaml` (see `provenance/settings.py`). An example file for running the webapp with the local test server is `custom_settings_example.yaml`, which you can just copy for local setup:

```
cp custom_settings_example.yaml custom_settings.yaml
```

Start django's test server in the usual way:

```
python manage.py runserver
```

and point a web browser to `localhost:8000`. Note that you can also provide a different port as additional argument to manage.py.

The webapp should be visible in the browser and it should even work offline, since all libraries are stored in the directory: `provenance-rave/provapp/static`. For deploying the webapp on an apache webserver, see below.

## Deploying the webapp on an apache server with `mod_wsgi`.
* Follow the installation steps on the web server, i.e. create a directory, clone the sources from GitHub, create a virtual environment, activate it and install the requirements. Then proceed as follows:

* If `mod_wsgi` is not yet installed, install it with:
    ```
    sudo apt-get install libapache2-mod-wsgi
    ```
    and enable the module with:
    ```
    sudo a2enmod wsgi
    ```

* Collect static files:
    - `source env/bin/activate`
    - `cd provenance-rave`
    - `python manage.py collectstatic`
    - You may be asked, if you want to overwrite existing files - check the given paths and type 'yes' to confirm.
    - Adjust file permissions, if needed (see next step)

* Make sure that the webserver-user has read (maybe also write) permission to this directory. On Debian systems you can achieve this using:
    - `sudo chown -R apache:apache /srv/provenance-rave`
    - on Ubuntu, the user is called `www-data`.
  - you may need to repeat this each time you do `collectstatic`

* Add a virtual host or an alias to your server configuration. Here's an example for a configuration on Debian using an alias (provenance-cosmosim), which you need to add to the config file at `/etc/httpd/conf.d/vhosts.conf`:

    ```
    <VirtualHost *:80>
    [...]

        # provenance test webapp
        Alias "/provenance-rave/static" "/srv/provenance-rave/provenance-rave/static/"
        <Directory "/srv/provenance-rave/provenance-rave/static/">
            Require all granted
        </Directory>

        WSGIDaemonProcess provenance-rave-app python-home=/srv/provenance-rave/env
        WSGIProcessGroup provenance-rave-app
        WSGIScriptAlias /provenance-rave /srv/provenance-rave/provenance-rave/provenance/wsgi.py process-group=provenance-rave-app
        <Directory "/srv/provenance-rave/provenance-rave/provenance">
            <Files wsgi.py>
                Require all granted
            </Files>
        </Directory>

    </VirtualHost>
    ```
    This uses a separate process group for the wsgi demon, so that multiple django instances can be installed on the same server.

* If you use a new port instead of an alias, do not forget to add `Listen 8111` (replace with your own port no.) to your webserver configuration (e.g. ports.conf)

* Enter your hostname to ALLOWED_HOSTS in `provenance/settings.py`,if it's not yet there already. E.g. for the localhost:
    - `ALLOWED_HOSTS = [u'127.0.0.1', u'localhost']`

* If using an alias (WSGIScriptAlias), do not forget to add it to the STATIC_URL in settings.py:
  `STATIC_URL = '/provenance-cosmosim/static/'`

* Reload the webserver, e.g. on Debian: `service httpd reload`

* Now open your web browser at the server specific address (e.g. http://localhost:8111/ or http://localhost/provenance-cosmosim/) and test the web application!
## Get a model graph
If the `graphviz` library is installed additionally, an image of the models and their relations can be created automatically with:

```shell
python manage.py graph_models provapp -o provenance-models.png
```

This produces an image file `provenance-models.png`, which shows all models from provapp with their attributes and relations. Other output formats like `pdf` or `svg` are also supported.

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


