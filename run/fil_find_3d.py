'''

'''
import sys
from astropy.io import fits
import numpy as np
import pickle
import process_cube
import mask_obj_node_tree as maskTree
fil_finder_dir = '/Users/larryli/Documents/CC/16-17/research/GALFA_filfind/fil_finder'
sys.path.append(fil_finder_dir)
import filfind_class as filfind


def findNewFullTree(root_node, overlap_thresh, reverse=False, verbose=False):
    new_tree = maskTree.newTreeFromNode(root_node, verbose=verbose)
    new_tree = findAllChildren(new_tree, overlap_thresh, reverse=reverse, verbose=verbose)

    # print new_tree.root_node.corners
    return new_tree


def findAllChildren(tree, overlap_thresh, reverse=False, verbose=False):
    start_v = tree.root_v_slice
    adv = 1
    if reverse:
        adv = -1
    v_slice = start_v + adv
    while v_slice < v_range[1]:
        if v_slice not in nodes_by_v_slice or len(nodes_by_v_slice[v_slice]) == 0:
            tree.has_ended = True
            break
        else:
            children_added = []
            if verbose:
                print "Corners of old nodes" + str(tree.getLastNode().corners)
            # sort keys in descending valye
            for i in sorted(nodes_by_v_slice[v_slice].keys(), reverse=True):
                if nodes_by_v_slice[v_slice][i].visited == False:
                    if tree.getLastNode().checkMaskOverlap(nodes_by_v_slice[v_slice][i], overlap_thresh):
                        children_added.append(i)
                        if verbose:
                            print "Corners of matched children" + str(nodes_by_v_slice[v_slice][i].corners)

            print "\t\t %d children found on slice %d" % (len(children_added), v_slice)
            if len(children_added) == 1:
                nodes_by_v_slice[v_slice][children_added[0]].visited = True
                print "\t\t\t %d - %d marked as visited" % (v_slice, children_added[0])
                tree.addNodeOnNewVChannel(nodes_by_v_slice[v_slice][children_added[0]])
                v_slice += adv
                continue
            elif len(children_added) > 1:
                first_node = nodes_by_v_slice[v_slice][children_added[0]]
                print "\t\t\t %d - %d marked as visited" % (v_slice, children_added[0])
                for j in children_added:
                    first_node.mergeNode(nodes_by_v_slice[v_slice][j])
                    nodes_by_v_slice[v_slice][j].visited = True
                first_node.visited = True
                tree.addNodeOnNewVChannel(first_node)
                v_slice += adv
                continue
            elif len(children_added) == 0:
                tree.has_ended = True
                break

    return tree


def createIntIntensityMap(v_min, v_max):
    int_intensity = np.zeros((y_dim, x_dim))

    print int_intensity.shape
    print v_min, v_max
    for v in range(v_min, v_max):
        int_intensity = int_intensity + cut_cube[v, :, :]

    return int_intensity


cube_dir = '../data/'
cube_name = 'usharpbg30.fits'

'''
v_range = [12,21]
y_range = [850, 1120]
x_range = [2230, 2600]
'''

'''
v_range = [0,9]
y_range = [750, 950]
x_range = [1900, 2600]
'''

# for the entire cube
v_range = [0,36]
y_range = [0, 1150]
x_range = [0, 2600]

x_dim = x_range[1] - x_range[0]
y_dim = y_range[1] - y_range[0]


full_cube, hdr = fits.getdata(cube_dir + cube_name, header=True)

# full cube dimentions
full_cube_shape = full_cube.shape
full_v_channel_count = full_cube_shape[0]
full_y_pixel_count = full_cube_shape[1]
full_x_pixel_count = full_cube_shape[2]

# cut cube based on provided x&y dimentions
cut_cube = full_cube[:, y_range[0]:y_range[1], x_range[0]:x_range[1]]


recover_pickle_path1 = 'pickled_dicts/usharpbg30[0, 36][1300, 2600][600, 1150].p'
recover_pickle_path2 = 'pickled_dicts/usharpbg30[5, 12][1600, 2400][600, 1100].p'
recover_pickle_path3 = 'pickled_dicts/usharpbg30[6, 10][1900, 2600][750, 950].p'
recover_pickle_path4 = 'pickled_dicts/usharpbg30[8, 10][1900, 2600][750, 950].p'
recover_pickle_path5 = 'pickled_dicts/usharpbg30[8, 9][1900, 2600][750, 950].p'
recover_pickle_path6 = 'pickled_dicts/usharpbg30[0, 36][0, 2600][0, 1150].p'

recover_path = recover_pickle_path6
nodes_by_v_slice = pickle.load(open(recover_path, 'rb'))

nodes_by_tree = {}
overlap_thresh = .75

reverse_find = True

for v in sorted(nodes_by_v_slice.keys(), reverse=reverse_find):
    if v not in nodes_by_v_slice:
        print "\n\nSOMETHING WENT WRONG"
        sys.exit()

    print "on v slice %d" % v

    if v == sorted(nodes_by_v_slice.keys())[-1]:
        for i in sorted(nodes_by_v_slice[v].keys(), reverse=True):
            print "\ton mask %d" % i

            new_full_tree = findNewFullTree(nodes_by_v_slice[v][i], overlap_thresh, reverse=reverse_find)
            nodes_by_tree[new_full_tree.getTreeMaskSize2D()] = new_full_tree

    else:
        for i in sorted(nodes_by_v_slice[v].keys(), reverse=True):
            print "\ton mask %d" % i

            if nodes_by_v_slice[v][i].visited == True:
                print "\t   visited"
                continue
            else:
                new_full_tree = findNewFullTree(nodes_by_v_slice[v][i], overlap_thresh, reverse=reverse_find)
                nodes_by_tree[new_full_tree.getTreeMaskSize2D()] = new_full_tree

print len(np.where(nodes_by_tree.keys) > 1000)
