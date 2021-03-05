'''
Python script to run the filfind algorithm on all velocity slices of the GALFA
cube

LL2016
'''


# imports
import sys
from astropy.io import fits
import numpy as np
import astropy.units as u #currently not used
import mask_obj_node as maskNode
import mask_obj_node_tree as maskTree
fil_finder_dir = '/Users/larryli/Documents/CC/16-17/research/GALFA_filfind/fil_finder'
sys.path.append(fil_finder_dir)
import filfind_class as filfind


# import cube
cube_dir = '../data/'
cube_name = 'usharpbg30.fits'
full_cube, hdr = fits.getdata(cube_dir + cube_name, header=True)

# full cube dimentions
full_cube_shape = full_cube.shape
full_v_channel_count = full_cube_shape[0]
full_y_pixel_count = full_cube_shape[1]
full_x_pixel_count = full_cube_shape[2]

print "\n\tThere are %d velocity channels in total" % full_v_channel_count
print "\n\tThe full image is %d by %d pixels" % (full_x_pixel_count, full_y_pixel_count)

# cut cube based on provided dimentions in argv
v_range = [int(sys.argv[1]), int(sys.argv[2])]
y_range = [int(sys.argv[3]), int(sys.argv[4])]
x_range = [int(sys.argv[5]), int(sys.argv[6])]


cut_cube = full_cube[:, y_range[0]:y_range[1], x_range[0]:x_range[1]]

# run though the slices in v_range and find masks
# store masks in nodes, and all nodes in a v slice in one list
# store that list in dict with v as key
nodes_by_v_slice = {}
for v in xrange(v_range[0], v_range[1]):
    v_slice = cut_cube[v, :, :]
    nodes_in_slice = []
    print "\n\n\tworking on velocity slice %d" % v

    # puts slice into filfind
    fils = filfind.fil_finder_2D(v_slice, header=hdr, beamwidth=10.0, glob_thresh=20,
                                 distance=100, flatten_thresh=95, standard_width=1.1,
                                 size_thresh=1000)
    # set verbose to true for things
    # note size_thresh, adapt_thresh, smooth_size, fill_hole_size can all be set by args
    mask_objs = fils.create_mask(verbose=False, regrid=False, border_masking=True,
                                 save_png=True, run_name=str(v), output_mask_objs=True)

    # for all masks returns put them in a list of mask_obj_nodes
    if mask_objs[0] == 0:
        print "\n\tNO objects in slice %d" % v
    else:
        for i in range(0, len(mask_objs[0])):
            this_mask_node = maskNode.MaskObjNode(mask_objs[0][i], mask_objs[1][i], v)
            nodes_in_slice.append(this_mask_node)

    # put that list of mask_obj_nodes into a dict with v as key
    nodes_by_v_slice[v] = nodes_in_slice

# analysis and organize the dict of list of nodes into trees of nodes
nodes_by_tree = []
for v in xrange(v_range[0], v_range[1] + 1):
    if v not in nodes_by_v_slice:
        print "\n\nSOMETHING WENT WRONG"
        sys.exit()

    nodes_in_slice = nodes_by_v_slice[v]

    for i in range(0, len(nodes_in_slice)):
        this_node = nodes_in_slice[i]
        if this_node.visited == False:
            this_node.visited = True

            new_tree = maskTree.MaskObjNodeTree(this_node)



