"""
Finds trees from dictionaries of nodes

"""
import pickle
import argparse
import glob
from astropy.io import fits
from cube_fil_finder.util import tree_dict_util
from cube_fil_finder.galfa import galfa_const


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--directory', default=None,
                        help="parent directory of the nodes dictionaries")
    parser.add_argument('-s', '--start', default=None, type=int,
                        help="starting v slice")
    parser.add_argument('-e', '--end', default=None, type=int,
                        help="ending v slice")
    parser.add_argument('-v', '--verbose', action='store_true',
                        help="increase output verbosity")
    args = parser.parse_args()

    file_dir = args.directory if args.directory else '../../pickled_dicts/full_sky_gaussian_30_1.0/'
    starting_v = args.start if args.start and args.start >= galfa_const.GALFA_SELECT_V_SLICES_RANGE[0] else galfa_const.GALFA_SELECT_V_SLICES_RANGE[0]
    ending_v = args.end if args.end and args.end <= galfa_const.GALFA_SELECT_V_SLICES_RANGE[1] else galfa_const.GALFA_SELECT_V_SLICES_RANGE[1]

    pickle_common_name = galfa_const.GALFA_SLICE_COMMON_NAME

    # get sample header for tree finding algorithm
    sample_slice_full_name = '/Volumes/LarryExternal1/Research_2017/GALFA_slices_backup/umask_gaussian_30/GALFA_HI_W_S0955_V-050.4kms_umask.fits'
    sample_hdr = fits.getheader(sample_slice_full_name)

    # find the full dictionary paths
    vs = range(starting_v, ending_v + 1)
    node_dict_full_paths = []
    pickle_name = file_dir + pickle_common_name
    for v in vs:
        if v // 100 < 10:
            glob_pickle_name = pickle_name + '0' + str(v) + '*'
        else:
            glob_pickle_name = pickle_name + str(v) + '*'

        if args.verbose:
            print "\t searching for: {0}".format(glob_pickle_name)
        true_pickle_name = glob.glob(glob_pickle_name)[0]
        node_dict_full_paths.append(true_pickle_name)
        if args.verbose:
            print "\t found: {0}".format(true_pickle_name)

    # run tree finding algorithm
    all_trees = tree_dict_util.find_all_trees_from_slices(vs, node_dict_full_paths, sample_hdr, verbose=args.verbose)

    save_dir = 'pickled_dicts/third_batch'
    save_name = 'all_trees.p'
    save_path = save_dir + save_name

    pickle.dump(all_trees, open(save_path, 'wb'))


if __name__ == '__main__':
    main()
