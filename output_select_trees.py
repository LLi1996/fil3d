'''
script to print the outline of select trees for further investigation
'''

import pickle
import argparse
from cube_fil_finder.vis import tree_vis as vis


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', default=None,
                        help="path of the tree dictionary")
    parser.add_argument('-l', '--length', default=1, type=int,
                        help="length (v) of tree has to be greater than this")
    parser.add_argument('-s', '--size', default=None, type=int,
                        help="size (pix) of tree has to be greater than this")
    parser.add_argument('-v', '--verbose', action='store_true',
                        help="increase output verbosity")
    args = parser.parse_args()

    save_fig_dir = '/Users/larryli/Documents/CC/16-17/research/GALFA_filfind/vis_out/'

    tree_dict_path = args.path if args.path else '../pickled_dicts/second_batch/all_trees.p'
    length_thresh = args.length
    size_thresh = args.size if args.size else 0

    trees = pickle.load(open(tree_dict_path, 'rb'))
    if args.verbose:
        print "\nloading {} trees".format(len(trees))
    cut_keys = []

    for k in trees:
        this_tree = trees[k]
        if this_tree.getTreeMaskedArea2D() > size_thresh and this_tree.getTreeAspectRatio() > length_thresh:
            cut_keys.append(k)

    cut_keys_count = len(cut_keys)
    if args.verbose:
        print "{} trees left after selection".format(cut_keys_count)

    processed_count = 1
    for k in cut_keys:
        if args.verbose:
            print "printing image of tree: {0}, {1} of {2} trees".format(k, processed_count, cut_keys_count)
        vis.vis_tree_shadow(trees[k], k, save_fig=True, save_dir=save_fig_dir)
        processed_count += 1


if __name__ == '__main__':
    main()
