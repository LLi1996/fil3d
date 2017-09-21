'''
This takes in a GALFA cube and processes it into a dict of dict of masks
'''

# imports
from astropy.io import fits
from cube_fil_finder.structs import util as struct_util
from cube_fil_finder.util import cube_util
import filfind_class as filfind
import glob
import mask_obj_node as maskNode
import pickle


def preprocess_cube_filfind_struct(file_dir, file_name, v_range, x_range, y_range,
                                   save_struct=True, verbose_process=False, verbose=True):
    '''
    Takes a GALFA data cube file, cuts it to the specified dimentions, and
    processes it slice by slice to find strucutres on each v slice with filfind.
    Each mask found by filfind on a single v slice is put into a dict with its
    masked_area_size as key and each dict is then put into a dict with its v
    index as key. The overall structure is either returned or pickled.
    '''

    # import cube
    cube_dir = file_dir
    cube_name = file_name
    full_cube, hdr = fits.getdata(cube_dir + cube_name, header=True)

    # full cube dimentions
    full_cube_shape = full_cube.shape
    full_v_channel_count = full_cube_shape[0]
    full_y_pixel_count = full_cube_shape[1]
    full_x_pixel_count = full_cube_shape[2]

    if verbose:
        print "\tThere are %d velocity channels in total" % full_v_channel_count
        print "\tThe full image is %d by %d pixels" % (full_x_pixel_count, full_y_pixel_count)
        print "\tProcessing x=" + str(x_range) + ", y=" + str(y_range) + " in v=" + str(v_range)

    # cut cube based on provided x&y dimentions
    cut_cube = full_cube[:, y_range[0]:y_range[1], x_range[0]:x_range[1]]

    # run though the slices in v_range and find masks
    # store masks in nodes, and all nodes in a v slice in an dict by their masked_area_size
    # store that list in dict with v as key
    nodes_by_v_slice = {}
    for v in xrange(v_range[0], v_range[1]):
        v_slice = cut_cube[v, :, :]
        nodes_in_slice = {}
        if verbose:
            print "\n\tworking on velocity slice %d" % v

        nodes_in_slice = process_dataslice_filfind_struct(v_slice, hdr, v, verbose_process=verbose_process)

        if len(nodes_in_slice) == 0:
            print "\n\tNO objects in slice %d" % v

        # put that dict of mask_obj_nodes into a dict with v as key
        nodes_by_v_slice[v] = nodes_in_slice

    # exit options
    if save_struct:
        save_dir = 'pickled_dicts/'
        save_name = cube_name.rsplit('.', 1)[0] + str(v_range) + str(x_range) + str(y_range) + '.p'
        save_path = save_dir + save_name

        if verbose:
            print "saving struct at " + save_path

        pickle.dump(nodes_by_v_slice, open(save_path, 'wb'))
        return save_path

    else:
        return nodes_by_v_slice


def preprocess_singleslice_filfind_struct(file_dir, file_name, slice_v_index, x_range, y_range,
                                          umask=False, umask_radius=None, umask_filter='tophat',
                                          save_struct=False, verbose_process=False, verbose=True):
    '''
    Take a single GALFA data slice file, sharp mask it if necessary and then
    cut it to the specified dimentions,
    and processes it to find strucutres with filfind.
    Each mask found by filfind is put into a dict with its masked_area_size as
    key.

    The overall structure is either returned or pickled.
    '''
    # import slice
    full_slice, hdr = fits.getdata(file_dir + file_name, header=True)

    # full slice dimentions
    full_slice_shape = full_slice.shape
    full_y_pixel_count = full_slice_shape[0]
    full_x_pixel_count = full_slice_shape[1]

    if verbose:
        print "\tThe full image is %d by %d pixels" % (full_x_pixel_count, full_y_pixel_count)
        print "\tProcessing x=" + str(x_range) + ", y=" + str(y_range) + " in v=" + str(slice_v_index)

    # cut slice based on provided x&y dimentions
    cut_slice = full_slice[y_range[0]:y_range[1], x_range[0]:x_range[1]]

    if umask:
        cut_slice = cube_util.umask_and_save(cut_slice, hdr, '../data/umask_from_susan/', file_name, umask_radius, umask_filter)

    # find masks in slice
    # store masks in nodes, and all nodes in an dict by their masked_area_size
    if verbose:
        print "\n\tFilfind working on velocity slice %d" % slice_v_index

    nodes_in_slice = process_dataslice_filfind_struct(cut_slice, hdr, slice_v_index, verbose_process=verbose_process)

    if len(nodes_in_slice) == 0:
        print "\n\tNO objects in slice %d" % slice_v_index

    del full_slice

    # exit options
    if save_struct:
        save_dir = 'pickled_dicts/'
        save_name = file_name.rsplit('.', 1)[0] + '[' + str(slice_v_index) + ']' + str(x_range) + str(y_range) + '.p'
        save_path = save_dir + save_name

        if verbose:
            print "saving struct at " + save_path

        pickle.dump(nodes_in_slice, open(save_path, 'wb'))
        return save_path

    else:
        return nodes_in_slice


def preprocess_multislice_filfind_struct(file_dir, slice_common_name, v_index_range, x_range, y_range,
                                         umask=False, save_struct=True, verbose_process=False, verbose=True):
    '''
    Takes multiple GALFA data slice files. Usharp mask them if necessary, and
    runs filfind on the them.
    Each mask found by filfind on a single v slice is put into a dict with its
    masked_area_size as key and each dict is then put into a dict with its v
    index as key.

    The overall structure is either returned or pickled.
    '''
    file_name = file_dir + slice_common_name

    nodes_by_v_slice = {}
    for v in xrange(v_index_range[0], v_index_range[1]):
        if verbose:
            print "\t current v index is " + str(v)

        if v // 100 < 10:
            glob_file_name = file_name + '0' + str(v) + '*'
        else:
            glob_file_name = file_name + str(v) + '*'

        if verbose:
            print "\t searching for: " + glob_file_name

        true_file_name = glob.glob(glob_file_name)[0].rsplit('/', 1)[-1]
        full_slice, hdr = fits.getdata(true_file_name, header=True)

        nodes_in_slice = preprocess_singleslice_filfind_struct(file_dir, true_file_name,
                                                               v, x_range, y_range, umask=True)

        # put dict of mask_obj_nodes into a dict with v as key
        nodes_by_v_slice[v] = nodes_in_slice

    # exit options
    if save_struct:
        save_dir = 'pickled_dicts/'
        save_name = true_file_name.rsplit('.', 1)[0] + str(v_index_range) + str(x_range) + str(y_range) + '.p'
        save_path = save_dir + save_name

        if verbose:
            print "saving struct at " + save_path

        pickle.dump(nodes_by_v_slice, open(save_path, 'wb'))
        return save_path

    else:
        return nodes_by_v_slice


def process_dataslice_filfind_struct(data, hdr, slice_v_index, verbose_process=False):
    '''
    Takes a single 2D data slice and runs filfind on it. Filfind will return the
    masks of structures and each mask is put into its own node and into a dict
    with its masked_area_size as the key.

    Returns the dict
    '''
    assert data.ndim == 2
    # puts slice into filfind
    fils = filfind.fil_finder_2D(data, header=hdr, beamwidth=10.0, glob_thresh=20,
                                 distance=100, flatten_thresh=95, standard_width=.5,
                                 size_thresh=600)
    # note size_thresh, adapt_thresh, smooth_size, fill_hole_size can all be set by args
    mask_objs = fils.create_mask(verbose=verbose_process, regrid=False, border_masking=True,
                                 save_png=True, run_name=str(slice_v_index), output_mask_objs=True,
                                 test_mode=verbose_process)

    # put returned masks in a dict of mask_obj_nodes
    nodes_in_dataslice = {}
    if mask_objs[0] != 0:
        for i in range(0, len(mask_objs[0])):
            this_mask_node = maskNode.MaskObjNode(mask_objs[0][i], mask_objs[1][i], slice_v_index)
            struct_util.add_node_to_dict(this_mask_node, nodes_in_dataslice)

    return nodes_in_dataslice
