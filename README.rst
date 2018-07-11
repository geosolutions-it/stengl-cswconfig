STENGL - CSW Configurator
=========================

.. image:: http://2013.foss4g.org/wp-content/uploads/2013/01/logo_GeoSolutions_quadrato.png
   :target: https://www.geo-solutions.it/
   :alt: GeoSolutions
   :width: 50

*CSW Configurator*

.. image:: https://badge.fury.io/py/cswconfig.svg?service=github
   :target: http://badge.fury.io/py/cswconfig

.. image:: https://travis-ci.org/geosolutions-it/cswconfig.svg?service=github
   :alt: Build Status
   :target: https://travis-ci.org/geosolutions-it/cswconfig

.. image:: https://coveralls.io/repos/github/geosolutions-it/cswconfig/badge.svg?branch=master&service=github
   :alt: Coverage Status
   :target: https://coveralls.io/github/geosolutions-it/cswconfig?branch=master

If you are facing one or more of the following:
 * TODO,
 * TODO,

Setup the virtual environment
-----------------------------

To setup your project using a local python virtual environment, follow these instructions:

1. Prepare the Environment

  .. code:: bash

    git clone https://github.com/geosolutions-it/stengl-cswconfig.git -b master
    mkvirtualenv stengl

    cd stengl-cswconfig

2. Setup the Python Dependencies

  .. code:: bash

    pip install -r requirements.txt --upgrade
    pip install -e . --upgrade

Usage Examples
--------------

From the folder `cd stengl-cswconfig`

Edit the templates and settings `cswconfig/settings/settings.ini`

.. code:: bash

 python cswconfig/convert.py -f /mnt/d/data/gisdata/data/good/vector/san_andres_y_providencia_administrative.shp --abstract "Description of the dataset" --datadate "2018-07-10 13:43:22" --timezone "Europe/Rome" --topic-category "boundaries" --temporalstart "2017-01-01" --temporalend "2020-01-01" --output FILE

.. code:: bash

 python cswconfig/convert.py -f /mnt/d/data/gisdata/data/good/vector/san_andres_y_providencia_administrative.shp --abstract "Description of the dataset" --datadate "2018-07-10 13:43:22" --timezone "Europe/Rome" --topic-category "boundaries" --temporalstart "2017-01-01" --temporalend "2020-01-01" --output CSW

Contributing
------------

We love contributions, so please feel free to fix bugs, improve things, provide documentation. Just `follow the
guidelines <https://cswconfig.readthedocs.io/en/latest/contributing.html>`_ and submit a PR.

Requirements
------------

* Python 2.7, 3.4, 3.5, 3.6
* httplib2 >= 0.7.4
* regex <= 2016.7.21
* requests == 2.18.4
* simplejson <= 3.13.2
* pyproj >=1.9.5,<=1.9.5.1
* OWSLib == 0.16.0
* Shapely == 1.5.17
* Jinja2 == 2.10
* awesome-slugify == 1.6.5
* python-dateutil == 2.7.3
* pytz==2018.3
* pygdal == 2.2.1.3
