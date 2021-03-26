Installing Fil3D
================

.. toctree::

Installation
------------

Fil3D can `eventually` be installed via pip (recommended, not available yet):

.. code-block:: shell

    pip install fil3d


Or you can install directly from this repo by (this will always fetch ``HEAD``, not 100% working yet):

.. code-block:: shell

    pip install git+https://github.com/LLi1996/fil3d


Or you can install directly from this repo in editable mode (this will always fetch ``HEAD`` and might be useful
if you want to poke around the code as well):

.. code-block:: shell

    pip install -e git+https://github.com/LLi1996/fil3d#egg=fil3d


Or you can install with ``setup.py`` after cloning this repo locally by:

.. code-block:: shell

    python setup.py install


Requirements
------------

Requires:

    * astropy
    * matplotlib
    * numpy
    * scipy

Optional:

    * filfinder (`docs <https://fil-finder.readthedocs.io/en/latest/>`_)

