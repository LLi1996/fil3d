"""
Get width and other things WIP

"""
import glob
import pickle
import argparse

DROPBOX_GOOD_MASKS = '/Users/larryli/Dropbox/GALFA_filfind_yes_no_maybe/BATCH/yes!/'
PICKLE_ALL_TREES = '/Users/larryli/Documents/CC/16-17/research/3d_filfind/pickled_dicts/BATCH/all_trees.p'
PICKLE_CHOSEN = '/Users/larryli/Documents/CC/16-17/research/3d_filfind/pickled_dicts/BATCH/chosen_all_trees.p'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--batch', default='1',
                        help='run batch number')
    parser.add_argument('-g', '--good_mask_dir', default=None,
                        help='directory of good masks')
    parser.add_argument('-p', '--pickle_file', default=None,
                        help='file path of the pickle')
    parser.add_argument('-s', '--save_file', action='store_true',
                        help='save the result pickle')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='make verbose')
    args = parser.parse_args()

    if args.batch == '1':
        batch = 'first_batch'
    elif args.batch == '2':
        batch = 'second_batch'

    if args.verbose:
        print('\nWorking on {0}'.format(batch))

    good_mask_dir = args.good_mask_dir if args.good_mask_dir else DROPBOX_GOOD_MASKS.replace('BATCH', batch)
    pickle_file = args.pickle_file if args.pickle_file else PICKLE_ALL_TREES.replace('BATCH', batch)
    pickle_save = PICKLE_CHOSEN.replace('BATCH', batch)

    good_masks_keys = parse_files_into_mask_names(good_mask_dir, verbose=args.verbose)
    good_trees_dict = get_good_masks_from_pickle(pickle_file, good_masks_keys, verbose=args.verbose)

    if args.save_file:
        if args.verbose:
            print('Saving...')
        pickle.dump(good_trees_dict, open(pickle_save, 'wb'))
    else:
        return good_trees_dict


if __name__ == '__main__':
    main()
