'''
process GALFA slices into dicts of mask objects
'''
import argparse
import logging
import os
import glob
from fil3d.galfa import preprocess_cube
from fil3d.galfa import galfa_const
from fil3d.util import util
import datetime

SLICE_COMMON_NAME = 'GALFA_HI_W_S'

V_INDEX_RANGE = galfa_const.GALFA_SELECT_V_SLICES_RANGE

DEFAULT_DIR = '../data/unprocessed_slices_from_susan/'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--directory', default=None,
                        help="parent directory of the data")
    parser.add_argument('-u', '--umask', default=False,
                        help="unsharp masking")
    parser.add_argument('-s', '--start', default=V_INDEX_RANGE[0], type=int,
                        help="starting v slice")
    parser.add_argument('-e', '--end', default=V_INDEX_RANGE[1], type=int,
                        help="ending v slice")
    parser.add_argument('-xs', '--x_start', default=0, type=int,
                        help="starting x pix")
    parser.add_argument('-xe', '--x_end', default=galfa_const.GALFA_X_STEPS, type=int,
                        help="starting x pix")
    parser.add_argument('-ys', '--y_start', default=0, type=int,
                        help="starting x pix")
    parser.add_argument('-ye', '--y_end', default=galfa_const.GALFA_Y_STEPS, type=int,
                        help="starting x pix")
    parser.add_argument('-f', '--filter', default='gaussian',
                        help="filter type for umask")
    parser.add_argument('-r', '--radius', default=30, type=int,
                        help="radius for umask")
    parser.add_argument('-v', '--verbose', action='store_true',
                        help="increase output verbosity")
    parser.add_argument('--logging_level', default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])
    args = parser.parse_args()

    util.basic_logging_setup(level=args.logging_level)

    file_dir = os.path.abspath(args.directory) if args.directory else DEFAULT_DIR

    X_INDEX_RANGE = [args.x_start, args.x_end]
    Y_INDEX_RANGE = [args.y_start, args.y_end]

    logging.info('x index range: {0}, y index range {1}'.format(X_INDEX_RANGE, Y_INDEX_RANGE))

    logging.info('Starting multislice process')

    file_name = file_dir + SLICE_COMMON_NAME

    for v in xrange(args.start, args.end + 1):
        logging.info('on slice {0}'.format(v))

        if v // 100 < 10:
            glob_file_name = file_name + '0' + str(v) + '*'
        else:
            glob_file_name = file_name + str(v) + '*'

        logging.debug("searching for: {}".format(glob_file_name))
        true_file_name = glob.glob(glob_file_name)[0]
        logging.debug("found: {}".format(true_file_name))

        true_file_name = true_file_name.split('/')[-1]

        preprocess_cube.preprocess_singleslice_filfind_struct(file_dir, true_file_name, v,
                                                              X_INDEX_RANGE, Y_INDEX_RANGE,
                                                              umask=args.umask, umask_radius=args.radius, umask_filter=args.filter,
                                                              save_struct=True, verbose_process=False, verbose=args.verbose)


if __name__ == '__main__':
    main()
