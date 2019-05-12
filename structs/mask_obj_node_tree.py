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
        self.root_node = copy.deepcopy(node_obj)
        self.root_v_slice = node_obj.v_slice_index[0]

        self.node_list = [node_obj]
        self.length = 1

        self.has_ended = False

    def addNodeOnNewVChannel(self, new_node, verbose=False):
        if verbose:
            print "Adding node to root"
            print "Old corners: " + str(self.root_node.corners)
            print "New node's corners: " + str(new_node.corners)

        self.root_node.mergeNode(new_node)
        self.node_list.append(new_node)
        self.length += 1

        if verbose:
            print "New corners: " + str(self.root_node.corners)
        return self.length

    def addNodeOnSameVChannel(self, new_node):
        logging.debug("merging node to root")
        logging.debug("Old corners: " + str(self.root_node.corners))
        logging.debug("New node's corners: " + str(new_node.corners))

        # merging the new node into the root_node
        self.root_node.mergeNode(new_node)

        # merging the new node into the last node so len(self.node_list) == self.length
        self.getLastNode().mergeNode(new_node)

    def getNode(self, node_number):
        return self.node_list[node_number]

    def getLastNode(self):
        return self.getNode(self.length - 1)

    def getTreeMask(self):
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
    if verbose:
        print "\tnew tree!"
    if mark_as_visited:
        node.visited = True

    new_tree = MaskObjNodeTree(node)

    return new_tree
