import logging

import numpy as np

from fil3d.galfa import galfa_const
from fil3d.util import cube_util


class MaskObjNode(object):
    """
    The MaskObjNode class is made to contain a single mask and its corners.
    The mask and corner can be produced by FilFinder or any other filament finding code. You can also manually input
    masks and corners .

    Each instance takes in:
       #. a mask (2d np bit array)
       #. the corners of the mask indicating where the mask is located
       #. the index of the velocity channel where the mask is located

    It is important to note the difference between the area of a mask and the
    masked area: since the masks are always rectangles, the area of a mask is just
    calculated from dimensions of the corners. The masked area, however, is
    calculated by counting the amount of pixels that's masked (marked TRUE in
    the np array).
    """

    def __init__(self, mask_obj, corners, v_slice_index):
        """
        :param mask_obj: {np.array}
            2D bit mask.

        :param corners: {List[List, List]}
            Corners of mask. In [(top left)[i,j],(bottom right)[i,j]] format when (0, 0) is at top left. This usually
            translates to [[y0, x0], [y1, x1]] in np indexing.

        :param v_slice_index: {int}
            Index of the velocity channel.

        """

        self.mask = mask_obj
        corners = fix_boarder_corners(self.mask, corners)

        # corners are [(top left)[i,j],(bottom right)[i,j]]
        # organize corners into list of lists instead of list of tups and convert into [x,y]
        self.corners_original = corners
        self.corners = self.corners_original  # legacy
        self.corner_min = self.corners_original[0]
        self.corner_max = self.corners_original[1]
        for i in range(2):
            assert self.corner_max[i] > self.corner_min[i]
        # should really just use corners_original and stick to np indexing
        # for future references use self.corners_original
        # other fields preserved for backward compatibility

        self.v_slice_index = [v_slice_index]

        self.visited = False
        self.mask_size = self.checkAreaSize()
        self.masked_area_size = self.checkMaskedAreaSize()

    def merge_node(self, other_node):
        """
        Merge other_node with self.
        Append to self.v_slice_index if needed and create the combined OR mask of self.mask and other_node.mask.
        The combined or mask is set as the new self.mask and other attributes are fixed.

        :param other_node: {MaskObjNode}

        :return: {bool}
            True
        """
        if self.v_slice_index[-1] != other_node.v_slice_index[0]:
            self.v_slice_index.append(other_node.v_slice_index[0])

        if self.checkCornersOverlap(other_node) == False:
            logging.warning('corners don\'t overlap!' \
                            + '(fine if using mergeNode() to consolidate two nodes on the same velocity channel)')

        combined_or_mask = self.combineMask(other_node, merge_type='OR')
        combined_masked_area_size = self.checkMaskedAreaSize(combined_or_mask)
        new_corners = self.matchCorners(other_node)

        self.mask = combined_or_mask
        self.corners = new_corners
        self.corners_original = self.corners
        self.corner_min = self.corners[0]
        self.corner_max = self.corners[1]
        self.mask_size = self.checkAreaSize(new_corners)
        self.masked_area_size = combined_masked_area_size

        return True

    def mergeNode(self, other_node):
        """
        Alias for merge_node()
        """
        return self.merge_node(other_node)

    def check_mask_overlap(self, other_node, overlap_thresh):
        """
        First check if the corners of self.mask and other_node.mask overlap.
        If the corners do overlap (meaning some part of the two squares overlap) we then check if actual masks overlap.
        To check for actual overlap, a combined AND mask is first made, and the masked area calculated.
        The masked area of the combined AND mask is then compared to the masked area of the input masks.

        :param other_node: {MaskObjNode}

        :param overlap_thresh: {float}

        :return: {bool}
            True if the the overlap between the combined AND mask and _either_ of the masks is greater than
            overlap_thresh.

        """
        if self.checkCornersOverlap(other_node) == False:
            return False

        combined_and_mask = self.combineMask(other_node, merge_type='AND')
        combined_masked_area_size = self.checkMaskedAreaSize(combined_and_mask)

        if float(combined_masked_area_size) / float(self.masked_area_size) >= overlap_thresh:
            return True
        elif float(combined_masked_area_size) / float(other_node.masked_area_size) >= overlap_thresh:
            return True
        else:
            return False

    def checkMaskOverlap(self, other_node, overlap_thresh):
        """
        Alias for check_mask_overlap()
        """
        return self.check_mask_overlap(other_node=other_node, overlap_thresh=overlap_thresh)

    def combineMask(self, other_node, merge_type='AND'):
        """
        Merge self.mask and other_node.mask. The corners of the 2 masks are
        first matched to fined the smallest square that contains both masks,
        a new mask is then made to that dimention. Elements of the new mask are
        filled basked on the merge_type ('AND' or 'OR').

        Returns:
            the new combined mask
        """
        new_corners = self.matchCorners(other_node)
        m_dim = new_corners[1][0] - new_corners[0][0]
        n_dim = new_corners[1][1] - new_corners[0][1]

        combined_mask = np.zeros((m_dim, n_dim), dtype=bool)

        expanded_self_mask = self.expandMask(new_corners)
        expanded_other_mask = other_node.expandMask(new_corners)

        if merge_type == 'AND':
            combined_mask = np.bitwise_and(expanded_self_mask, expanded_other_mask)
        elif merge_type == 'OR':
            combined_mask = np.bitwise_or(expanded_self_mask, expanded_other_mask)

        return combined_mask

    def checkCornersOverlap(self, other_node):
        """
        Check if self.mask and other_node.mask have any overlap
        Arguments:
            other_node {MaskObjNode} -- other node
        Returns:
            bool -- true if overlap
        """
        # vertical mismatch
        if other_node.corner_max[0] <= self.corner_min[0] or other_node.corner_min[0] >= self.corner_max[0]:
            return False
        # horizontal mismatch
        if other_node.corner_max[1] <= self.corner_min[1] or other_node.corner_min[1] >= self.corner_max[1]:
            return False
        return True

    def matchCorners(self, other_node):
        """
        Compare the self.mask and other_node.mask and pick out the smallest
        square that contain both masks.
        Arguments:
            other_node {MaskObjNode} -- other node
        Returns:
            corners -- the corners of that square.
        """
        corner_min = [min(self.corner_min[i], other_node.corner_min[i]) for i in range(2)]
        corner_max = [max(self.corner_max[i], other_node.corner_max[i]) for i in range(2)]

        return [corner_min, corner_max]

    def checkMaskedAreaSize(self, mask=None):
        """
        Calculate the amount of pixels that are masked by self.mask. If a new
        mask is provided then that mask is used
        Keyword Arguments:
            mask {2d np.array of bool} -- mask
        Returns:
            int -- # of pixels masked (as opposed to the area of the mask)
        """
        if mask is None:
            mask = self.mask

        return np.size(np.where(mask == True)[0])

    def expandMask(self, new_corners):
        """
        Expand self.mask so its corners match the new_corners provided. Masks
        are paded with 0s with the numpy function pad()
        Arguments:
            new_corners {MaskObjNode.corners} -- new corners
        Returns:
            new expanded mask
        """
        mask = self.mask

        old_corners = self.corners_original
        # now assume that new_corners are passed in as np indexing
        i_pad_before = old_corners[0][0] - new_corners[0][0]
        i_pad_after = new_corners[1][0] - old_corners[1][0]
        j_pad_before = old_corners[0][1] - new_corners[0][1]
        j_pad_after = new_corners[1][1] - old_corners[1][1]
        return np.pad(mask, ((i_pad_before, i_pad_after), (j_pad_before, j_pad_after)), 'constant', constant_values=0)

    def checkAreaSize(self, corners=None):
        """
        Calculate the area of self.mask by looking at its dimentions from its
        corners. If corners are provided then an area based on that corner is
        calculated.
        Keyword Arguments:
            corners {MaskObjNode.corners} -- corners (default: {None})
        Returns:
            int -- the area of the mask (in pixels^2)
        """
        if corners is None:
            corners = self.corners

        return (corners[1][0] - corners[0][0]) * (corners[1][1] - corners[0][1])

    def getDimentions(self):
        """Calculate the pixel dimentions of the mask
        Returns:
            int, int -- width, height
        """
        height = self.corner_max[0] - self.corner_min[0]
        width = self.corner_max[1] - self.corner_min[1]

        assert width > 0, "width is 0 or negative"
        assert height > 0, "height is 0 or negative"

        return width, height

    def getAR(self):
        """Calculates the aspect ratio of the mask
        Returns:
            float -- aspect ratio
        """
        width, height = self.getDimentions()

        ar = float(width) / height

        if ar < 1:
            ar = float(height) / width

        assert ar >= 1, "Aspect Ratio is less than 1"

        return ar


def check_node_b_cutoff(node, hdr, b_cutoff=30):
    """checks if the node is within the b_cutoff range
    Arguments:
        node {mask_node} -- node obj
        hdr {fits.header} -- slice/cube FITS header
    Keyword Arguments:
        b_cutoff {int} -- latitude cutoff (default: {30})
    Returns:
        bool -- true if within cutoff, false if not
    """
    ys = [node.corner_min[0], node.corner_max[0]]
    xs = [node.corner_min[1], node.corner_max[1]]

    ras, decs = cube_util.index_to_radec(xs, ys, hdr)
    ls, bs = cube_util.radecs_to_lb(ras, decs)

    if bs[0] * bs[1] <= 0:
        return True

    if np.abs(bs[0]) >= b_cutoff and np.abs(bs[1]) >= b_cutoff:
        return False
    else:
        return True


def get_node_plot_corners(node):
    """gets the x y plot corners for matplotlib
    Arguments:
        node {mask_node} -- node obj
    """
    return [node.corner_min[0], node.corner_max[1], node.corner_min[1], node.corner_max[1]]


def fix_boarder_corners(mask, corners):
    """ fix when masks are larger than corners indicated when near boarder
    Arguments:
        mask {np.array} -- mask
        corners {list} -- of tuples
    """
    m_mask, n_mask = mask.shape
    corners = [list(corners[0]), list(corners[1])]
    if corners[1][0] - corners[0][0] != m_mask or corners[1][1] - corners[0][1] != n_mask:  # only check if issue
        if corners[0][0] == 0:
            corners[0][0] = -1
        if corners[0][1] == 0:
            corners[0][1] = -1
        if corners[1][0] == galfa_const.GALFA_Y_STEPS - 1:
            corners[1][0] = galfa_const.GALFA_Y_STEPS
        if corners[1][1] == galfa_const.GALFA_X_STEPS - 1:
            corners[1][1] = galfa_const.GALFA_X_STEPS
    return corners
