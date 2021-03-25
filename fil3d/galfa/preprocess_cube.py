'''
This takes in a GALFA slice/cube and processes it into dicts of masks

If requried, this will pre process the file by usharpmasking
'''

# imports
import logging
from astropy.io import fits
from astropy import units as u
import os
import pickle
import warnings
from fil3d.structs import util as struct_util
from fil3d.util import cube_util
from fil_finder import FilFinder2D
from fil3d.structs import mask_obj_node



def preprocess_cube_filfind_struct(file_dir, file_name, v_range, x_range, y_range,
                                   save_struct=True, verbose_process=False, verbose=True):
    ''' DEPRECATED
    Takes a GALFA data cube file, cuts it to the specified dimentions, and
    processes it slice by slice to find strucutres on each v slice with filfind.
    Each mask found by filfind on a single v slice is put into a dict with its
    masked_area_size as key and each dict is then put into a dict with its v
    index as key. The overall structure is either returned or pickled.
    '''
    warnings.warn('preprocess_cube_filfind_struct() deprecated use preprocess_singleslice_filfind_struct() instead',
                  DeprecationWarning)
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
                                          umask=False, umask_radius=None, umask_filter=None,
                                          save_struct=False, verbose_process=False, verbose=True):
    '''
    Take a single GALFA data slice file, unsharp mask it if necessary and then
    cut it to the specified dimentions,
    and processes it to find strucutres with filfind.
    Each mask found by filfind is put into a dict with its masked_area_size as
    key.

    The overall structure is either returned or pickled.
    '''
    # import slice
    full_slice, hdr = fits.getdata(file_dir + file_name, header=True)

    # full slice dimentions
    full_y_pixel_count, full_x_pixel_count = full_slice.shape


    logging.info("the full image is %d by %d pixels" % (full_x_pixel_count, full_y_pixel_count))
    logging.info("processing x=" + str(x_range) + ", y=" + str(y_range) + " in v=" + str(slice_v_index))

    # cut slice based on provided x&y dimentions
    cut_slice = full_slice[y_range[0]:y_range[1], x_range[0]:x_range[1]]

    if umask:
        cut_slice = cube_util.umask_and_save(cut_slice, hdr, '../data/umask_from_susan/', file_name, umask_radius, umask_filter)

    # find masks in slice
    # store masks in nodes, and all nodes in an dict by their masked_area_size
    logging.info('running initial filament finding on the image with filfinder ...')
    nodes_in_slice = process_dataslice_filfind_struct(cut_slice, hdr, slice_v_index, verbose_process=verbose_process)

    if len(nodes_in_slice) == 0:
        logging.warning('no objects found by filfinder in slice {0}'.format(slice_v_index))
    else:
        logging.info('found {0} objects in slice {1}'.format(len(nodes_in_slice), slice_v_index))

    del full_slice

    # exit options
    if save_struct:
        save_dir = '../../../pickled_dicts/'
        save_dir = os.path.abspath(save_dir)
        save_name = file_name.rsplit('.', 1)[0] + '[' + str(slice_v_index) + ']' + str(x_range) + str(y_range) + '.p'
        save_path = os.path.join(save_dir, save_name)

        logging.info('saving found structures at {0} ...'.format(save_path))
        pickle.dump(nodes_in_slice, open(save_path, 'wb'))
        return save_path

    else:
        return nodes_in_slice


def process_dataslice_filfind_struct(data, hdr, slice_v_index):
    '''
    Takes a single 2D data slice and runs filfind on it. Filfind will return the
    masks of structures and each mask is put into its own node and into a dict
    with its masked_area_size as the key.

    Returns the dict
    '''
    hdr['BUNIT'] = 'k'  # as opposed to 'k (tb)' which isn't recognized by astropy.units
    fils = FilFinder2D(data, header=hdr, distance=100. * u.pc, beamwidth=10 * u.arcmin)
    fils.preprocess_image(flatten_percent=95)
    standard_width = 0.1 * u.pc  # from experiments
    mask_objs, corners = fils.create_mask(smooth_size=standard_width / 2,
                                          adapt_thresh=standard_width * 2,
                                          size_thresh=(standard_width * 2) ** 2 * 8,
                                          border_masking=False, output_mask_objs=True)

    # put returned masks in a dict of mask_obj_nodes
    nodes_in_dataslice = {}
    if mask_objs is None:
        return nodes_in_dataslice
    else:
        for i in range(len(mask_objs)):
            this_mask_node = mask_obj_node.MaskObjNode(mask_objs[i], corners[i], slice_v_index)
            struct_util.add_node_to_dict(this_mask_node, nodes_in_dataslice)

    return nodes_in_dataslice
