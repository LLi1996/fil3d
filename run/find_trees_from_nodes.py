"""
Finds trees from dictionaries of nodes

"""
import pickle
import argparse
import glob
import os
import logging
from astropy.io import fits
from cube_fil_finder.util import tree_dict_util
from cube_fil_finder.galfa import galfa_const

DEFAULT_DIR = '../../pickled_dicts/full_sky_gaussian_30_1.0/'


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
    parser.add_argument('--logging_level', default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])
    args = parser.parse_args()

    # logging setup
    fmt = '%(asctime)s %(levelname)s (%(module)s.%(funcName)s()): %(message)s'
    logging.basicConfig(format=fmt, level=args.logging_level)

    file_dir = os.path.abspath(args.directory) if args.directory else DEFAULT_DIR
    starting_v = args.start if args.start and args.start >= galfa_const.GALFA_SELECT_V_SLICES_RANGE[0] else galfa_const.GALFA_SELECT_V_SLICES_RANGE[0]
    ending_v = args.end if args.end and args.end <= galfa_const.GALFA_SELECT_V_SLICES_RANGE[1] else galfa_const.GALFA_SELECT_V_SLICES_RANGE[1]

    common_pickle_name = galfa_const.GALFA_SLICE_COMMON_NAME

    logging.info('file_dir: {0}'.format(file_dir))
    logging.info('starting v index: {0}, ending v index: {1}'.format(starting_v, ending_v))

    # find the full dictionary paths
    vs = range(starting_v, ending_v + 1)
    node_dict_full_paths = []
    common_pickle_path = os.path.join(file_dir, common_pickle_name)
    logging.info('searching for paths of pickeled dictionaries of nodes')
    for v in vs:
        if v // 100 < 10:
            glob_picke_name = common_pickle_path + '0' + str(v) + '*'
        else:
            glob_picke_name = common_pickle_path + str(v) + '*'

        logging.debug("searching for: {0}".format(glob_picke_name))
        true_pickle_name = glob.glob(glob_picke_name)[0]
        node_dict_full_paths.append(true_pickle_name)
        logging.debug("found: {0}".format(true_pickle_name))

    exit()

    # run tree finding algorithm
    all_trees = tree_dict_util.find_all_trees_from_slices(vs, node_dict_full_paths, verbose=args.verbose)

    tree_dict_util.end_noncontinuous_trees(all_trees, galfa_const.GALFA_SELECT_V_SLICES_RANGE[1] + 1)
    tree_dict_util.delete_short_dead_trees(all_trees, verbose=args.verbose)

    save_dir = '../../pickled_dicts/fourth_batch/'
    save_name = 'all_trees.p'
    save_path = save_dir + save_name

    pickle.dump(all_trees, open(save_path, 'wb'))


if __name__ == '__main__':
    main()
