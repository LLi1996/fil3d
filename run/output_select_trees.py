"""
script to print the masks of select trees for further investigation

LL2017
"""

import pickle
import argparse
from fil3d.vis import tree_vis as vis
from fil3d.util import moments as moments


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', default=None,
                        help="path of the tree dictionary")
    parser.add_argument('-l', '--length', default=1, type=int,
                        help="length (v) of tree has to be greater than this")
    parser.add_argument('-s', '--size', default=5000, type=int,
                        help="size (pix) of tree has to be greater than this")
    parser.add_argument('-r', '--roundness', default=0.0625, type=float,
                        help='roundness of mask has to be less than this')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help="increase output verbosity")
    args = parser.parse_args()

    save_fig_dir = '/Users/larryli/Documents/CC/16-17/research/3d_filfind/vis_out/'

    tree_dict_path = args.path if args.path else '../../pickled_dicts/second_batch/all_trees.p'
    length_thresh = args.length
    size_thresh = args.size if args.size else 0
    roundness_thresh = args.roundness if args.roundness else 1

    trees = pickle.load(open(tree_dict_path, 'rb'))
    if args.verbose:
        print(f"\nloading {len(trees)} trees")
    cut_keys = []

    for k in trees:
        this_tree = trees[k]
        if this_tree.getTreeMaskedArea2D() > size_thresh and this_tree.length > length_thresh:
            if args.roundness is None or moments.get_tree_mask_orientation_info(this_tree)[4] < roundness_thresh:
                cut_keys.append(k)

    cut_keys_count = len(cut_keys)
    if args.verbose:
        print(f"{cut_keys_count} trees left after selection")

    processed_count = 1
    for k in cut_keys:
        if args.verbose:
            print(f"printing image of tree: {k}, {processed_count} of {cut_keys_count} trees")
        vis.vis_tree_shadow(trees[k], k, save_fig=True, save_dir=save_fig_dir)
        processed_count += 1


if __name__ == '__main__':
    main()
