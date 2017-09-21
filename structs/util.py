"""
Utility functinos related to nodes and trees

LL2017
"""


def node_key_hash(original_key):
    """Hash them node keys
    in format: masked_area_size + '_' + some number
    Arguments:
        original_key {str} -- original key with overlap
    """
    key_base = original_key.rsplit('_', 1)[0]
    key_num = int(original_key.rsplit('_', 1)[1])

    key_num += 1

    new_key = key_base + '_' + str(key_num)
    return new_key


def node_key_unhash(key):
    """Unhash them node keys
    Arguments:
        key {str} -- hashed node key
    Returns:
        int, int -- masked_area_size, number
    """
    key_decomp = key.rsplit('_')

    masked_area_size = int(key_decomp[0])
    number = key_decomp[1]

    return masked_area_size, number


def add_node_to_dict(node, dictionary):
    """Adds the node to the dictionary
    prevents key overlapping by hashing
    Arguments:
        node {MaskObjNode} -- node to be added
        dictionary {dict} -- of nodes
    """
    key = str(node.masked_area_size)
    key += '_0'

    while key in dictionary:
        key = node_key_hash(key)

    dictionary[key] = node


def tree_key_hash(original_key):
    """Hash them tree keys
    in format: masked_area_size + '_' + starting_v + '_' + some number
    Arguments:
        original_key {str} -- unhashed tree key
    """
    key_base = original_key.rsplit('_', 1)[0]
    key_num = int(original_key.rsplit('_', 1)[1])

    key_num += 1

    new_key = key_base + '_' + str(key_num)
    return new_key


def tree_key_unhash(key):
    """Unhash them tree keys
    Arguments:
        key {str} -- hashed tree key
    Returns:
        int, int, int -- masked_area_size, starting_v, number
    """
    key_decomp = key.rsplit('_')

    masked_area_size = int(key_decomp[0])
    starting_v = int(key_decomp[1])
    number = key_decomp[2]

    return masked_area_size, starting_v, number


def add_tree_to_dict(tree, dictionary):
    """Adds a tree to the dictionary
    prevents key overlaps by hasing
    Arguments:
        tree {MaskObjNodeTree} -- tree to be added
        dictionary {dict} -- of trees
    """
    key = str(tree.getTreeMaskedArea2D())
    key += '_' + str(tree.getTreeStartingVelocity()) + '_0'

    while key in dictionary:
        key = tree_key_hash(key)

    dictionary[key] = tree


def sorted_node_dict_keys(node_dict_keys, descending=True):
    """Sort the node dict keys by masked area size
    Arguments:
        tree_dict_keys {list} -- of hashed node keys
    Keyword Arguments:
        descending {bool} -- if reverse sort (default {True})
    """
    mapped_keys = map(lambda k: (k, node_key_unhash(k)[0]), node_dict_keys)
    sorted_mapped_keys = sorted(mapped_keys, key=lambda x: x[1], reverse=descending)
    return map(lambda (k, v): k, sorted_mapped_keys)
