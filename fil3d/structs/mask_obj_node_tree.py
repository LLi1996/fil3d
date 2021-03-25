import logging
import copy
import numpy as np


class MaskObjNodeTree:
    """
    This node_tree object is made to contain the nodes which contain masks
    produced by fil_finder.
    Each tree contains a starting node and a string of nodes which define the
    tree.

    The first node contains the aggregated mask and is merged with each a
    subsequent addition
    """

    def __init__(self, node_obj):
        """Initiate a new MaskObjNodeTree object based on the starting node.

        :param node_obj: Starting node of the tree.
        :type node_obj: MaskObjNode
        """
        self.root_node = copy.deepcopy(node_obj)
        self.root_v_slice = node_obj.v_slice_index[0]

        self.node_list = [node_obj]
        self.length = 1

        self.has_ended = False

    def addNodeOnNewVChannel(self, new_node, verbose=False):
        """The "standard" procedure of adding a new node onto a tree.

        We take a new node and:

        #. merge the node into the tree root node (to capture the overall "shadow" of the tree)
        #. append the node to the list of nodes on the tree
        #. assume it is on the "next" velocity channel and append the length of the tree by 1

        :param new_node: New node to be added onto the "next" velocity channel.
        :type new_node: MaskObjNode
        :param verbose: (optional) Currently not used. Defaults to ``False``.
        :type verbose: bool

        :return: The length of the tree post adding the node on the new velocity channel (this should equal the old \
        length + 1).
        """
        logging.debug("Adding node to tree (new velocity channel)")
        logging.debug("New node's corners: " + str(new_node.corners))

        logging.debug("Old root node corners: " + str(self.root_node.corners))

        # merging the new node into the root_node
        self.root_node.merge_node(new_node)

        # adding the new node to the list of nodes
        self.node_list.append(copy.deepcopy(new_node))
        self.length += 1

        logging.debug("New root node corners: " + str(self.root_node.corners))

        return self.length

    def addNodeOnSameVChannel(self, new_node):
        """The "special" procedure of adding a node to a tree when the tree already has a node on that velocity channel.

        In this special case we need to preserve the design that a given node at index i of the node list is
        representative of all the nodes that belong to this tree on that velocity channel (the channel being the tree
        starting velocity channel + i). To do this we take the new node and:
        #. merge the node into the tree root node (to capture the overall "shadow of the tree)
        #. merge the node with the last node in the list of nodes on the tree (with the assumption that the new node \
        and the last node are on the same velocity channel)

        :param new_node: New node to be added onto the same velocity channel as the last node.
        :type new_node: MaskObjNode

        :return: The length of the tree post adding the node on the same velocity channel (this should equal what \
        it was before.
        """
        logging.debug("Adding node to tree (same velocity channel)")
        logging.debug("New node's corners: " + str(new_node.corners))

        logging.debug("Old root node corners: " + str(self.root_node.corners))
        # merging the new node into the root_node
        self.root_node.merge_node(new_node)

        # merging the new node into the last node so len(self.node_list) == self.length
        self.getLastNode().mergeNode(new_node)

        logging.debug("New root node corners: " + str(self.root_node.corners))

        return self.length


    def getNode(self, node_number):
        """Return the node at a given index.

        :param node_number: Index.
        :type node_number: int

        :rtype: MaskObjNode
        """
        return self.node_list[node_number]

    def getLastNode(self):
        """Return the last node.

        :rtype: MaskObjNode
        """
        return self.getNode(self.length - 1)

    def getTreeMask(self):
        """Return the mask that contains the overall area/shadow of the tree.

        :rtype: NumPy.Array
        """
        return self.root_node.mask

    def getTreeMaskSize2D(self):
        return self.root_node.mask_size

    def getTreeMaskedArea2D(self):
        return self.root_node.masked_area_size

    def getTreeVelocityRange(self):
        return np.arange(self.root_v_slice, self.root_v_slice + self.length)

    def getTreeStartingVelocity(self):
        return self.root_v_slice

    def getTreeAspectRatio(self):
        return self.root_node.getAR()

    def removeLastNode(self):
        pass

    def visitAllNodes(self):
        pass


def newTreeFromNode(node, mark_as_visited=True, verbose=False):
    logging.info('constructing new tree from node')
    if mark_as_visited:
        node.visited = True

    new_tree = MaskObjNodeTree(node)

    return new_tree


def back_merge_trees(base_tree, other_tree):
    """

    :param base_tree:
    :param other_tree:
    :return:
    """
    # assuming that the base tree and the other tree are on the same "latest" velocity channel
    if base_tree.length < other_tree.length:
        # this is the "flipped" back merge configuration
        temp = base_tree
        base_tree = other_tree
        other_tree = temp

    v_channel_diff = base_tree.length - other_tree.length
    merged_tree = newTreeFromNode(base_tree.getNode(0))
    for base_tree_node_index in range(base_tree.length):
        if base_tree_node_index != 0:
            # skipping the 0 case cause we already initiated the meged_tree from the base_tree 0th node
            merged_tree.addNodeOnNewVChannel(base_tree.getNode(base_tree_node_index))

        other_tree_node_index = base_tree_node_index - v_channel_diff
        if other_tree_node_index >= 0:
            merged_tree.addNodeOnSameVChannel(other_tree.getNode(other_tree_node_index))

    return merged_tree