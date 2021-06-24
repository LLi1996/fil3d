Installing Fil3D
================

.. toctree::

Installation
------------

Fil3D can `eventually` be installed via pip (recommended, not available yet):

.. code-block:: shell

    pip install fil3d


Or you can install directly from this repo (this will always fetch ``HEAD`` - do this for now if you just want to
use the package):

.. code-block:: shell

    pip install git+https://github.com/LLi1996/fil3d


Or you can install directly from this repo in editable mode (this will always fetch ``HEAD`` - do this if you want to
use the package and maybe poke around the code as well):

.. code-block:: shell

    pip install -e git+https://github.com/LLi1996/fil3d#egg=fil3d


Of course you can also just install with ``setup.py`` after cloning this repo locally (this is the same as pip install
-e but with more steps):

.. code-block:: shell

    git clone https://github.com/LLi1996/fil3d.git
    cd fil3d
    python setup.py install


Requirements
------------

Requires:

    * astropy
    * matplotlib
    * numpy
    * scipy

Optional:

    * FilFinder (`docs <https://fil-finder.readthedocs.io/en/latest/>`_)


Quickstart
----------

We separate data and masks. Data in this case refer to data cubes, data slices, FITS files, numpy arrays, etc. -
whatever you use to to store your data. Masks in this case refers to a 2D numpy array bit-mask (and the associated
corners of that mask). Masks are the primary objects in most parts of the program - velocity-aware mask objects are
compared, merged, and stacked to create representations (bounds) of filaments in 3D (P-P-V) space that we call trees.
When we need pixel values to analyse individual filaments, these collections of masks (trees) are used to pull values
out of whatever data storage systems / formats that you prefer.

2D mask container objects are the base units. A mask object can be instantiated with three components: 1) the 2D
bit mask (this is self-explanatory), 2) the corners which matches the dimensions of this 2D bit mask (this will be used
to locate the mask within the greater data slice/cube, so that this mask can be compared to other masks and this mask
object can be used to select data from your data files), and 3) the index of the velocity channel where this mask
belongs (it is important that you assign some sequential ordering to your velocity slices - it doesn't matter if you
choose ascending or descending - but note that mask objects which do not reside on neighboring velocity slices will not
be considered for matching later in the program).


Using your own masks
____________________

If you already have masks lying around, you can plug those into the base
:ref:`MaskObjNode-label`, like this:

.. code-block:: python

    import numpy as np
    from fil3d import MaskObjNode

    # some 4x4 mask, with 6 pixels ON and 10 pixels OFF
    mask = np.asarray([[0, 0, 0, 0],
                       [1, 1, 1, 0],
                       [0, 1, 1, 1],
                       [0, 0, 0, 0]], bool)

    # [[y0, x0], [y1, x1]] in numpy indexing, note our 4x4 mask needs to fit in the corners
    corners = [[0, 1],
               [4, 5]]
    # let's say this mask is for data residing on the third velocity slice in your collection
    v_index = 2

    mask_obj = MaskObjNode(mask, corners, v_index)


    # if you have multiple of these masks and their corners and velocity indexes:
    mask_obj_dict = {}
    for mask_obj in list_of_mask_objs:
        MaskObjNode.add_node_to_dict(mask_obj, mask_obj_dict)


Getting masks from FilFinder
____________________________

If you are using `FilFinder <https://fil-finder.readthedocs.io/en/latest/>`_, you can pluck the masks and corners from
``FilFinder2D`` objects that you've already created. To do so, you have to set ``capture_pre_recombine_masks=True`` at
object instantiation to enable the caching of masks before they're combined into a single skeleton.

Currently this feature is in preview for FilFinder 1.18 (as of 2021-06-24, the latest pip-installable version on pypi
is 1.17). Don't worry though - you can still access this feature by directly building FilFinder from the source repo
master like this:

.. code-block:: shell

    pip install git+https://github.com/e-koch/FilFinder


After running ``create_mask()`` with ``use_existing_mask=False``, you will be able to access the
``pre_recombine_mask_objs`` and ``pre_recombine_mask_corners`` properties of the instance. For this quick start
run-through, we'll be using a data cube with a few injected filaments located on the github repo under
``data/examples/fil_injection/``.

.. code-block:: python

    import numpy as np

    from astropy import units as u
    from astropy.io.fits import Header
    from fil_finder import FilFinder2D
    from fil3d import MaskObjNode

    # 50 x 300 x 500 data cube (v, y, x)
    data_cube = np.load('data/examples/fil_injection/fil_injection.npz')['data']

    # let's say the image fed into FilFinder resides on the third velocity slice in your collection
    v_index = 2
    data_slice = data_cube[v_index]

    # creating a fake header to make our lives a little easier
    hdr = Header(dict(
        CTYPE1='RA',
        CDELT1=-0.0166667,
        CTYPE2='DEC',
        CDELT2=0.0166667,
        BUNIT='K'
    ))
    # most of this follows the FilFinder2D docs
    fil = FilFinder2D(data_slice,
                      header=hdr,
                      distance=100. * u.pc,
                      beamwidth=10 * u.arcmin,
                      capture_pre_recombine_masks=True)
    fil.preprocess_image(flatten_percent=95)
    fil.create_mask()

    # there might be multiple masks in a single FilFinder2D instance
    # here we store them in a dictionary for ease of access, with an arbitrary numerical key
    mask_obj_dict = {}

    for i in range(len(fil.pre_recombine_mask_objs)):
        MaskObjNode.add_node_to_dict(MaskObjNode(fil.pre_recombine_mask_objs[i],
                                                 fil.pre_recombine_mask_corners[i],
                                                 v_index),
                                     mask_obj_dict)


Going from 2D masks to 3D trees
_______________________________

One of the main advantanges of working with masks is that we don't have to carry data around when we're performing mask
matching operations between velocity slices. For the purpose of this tutorial, we'll be using processed dictionaries of
masks for each velocity channel in the example data cube stored in github under
``data/examples/fil_injection/mask_dictionaries/``.

Using the process outlined in :ref:`MasksToTrees-label`, we match mask objects on neighboring velocity channels to
build "trees" in the 3D (P-P-V) space. The utility function ``find_all_trees_from_slices()`` can be used like this:


.. code-block:: python

    import pickle

    from fil3d.util.tree_dict_util import find_all_trees_from_slices

    velocity_channels = range(50)
    mask_dict_paths = [f'data/examples/fil_injection/mask_dictionaries/{i}.PICKLE' for i in range(50)]

    tree_dict = find_all_trees_from_slices(vs=velocity_channels,
                                           dict_full_paths=mask_dict_paths,
                                           overlap_thresh=.85)

This will return a dictionary of trees.


Using trees to access data
__________________________

WIP