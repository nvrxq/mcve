import torch
import numpy as np


def xy_to_cxcy(xy):
    """
    Convert bounding boxes from boundary coordinates (x_min, y_min, x_max, y_max) to center-size coordinates (c_x, c_y, w, h).
    :param xy: bounding boxes in boundary coordinates, a tensor of size (n_boxes, 4)
    :return: bounding boxes in center-size coordinates, a tensor of size (n_boxes, 4)
    """
    return torch.cat(
        [(xy[:, 2:] + xy[:, :2]) / 2, xy[:, 2:] - xy[:, :2]], 1  # c_x, c_y
    )  # w, h


def cxcy_to_xy(cxcy):
    """
    Convert bounding boxes from center-size coordinates (c_x, c_y, w, h) to boundary coordinates (x_min, y_min, x_max, y_max).
    :param cxcy: bounding boxes in center-size coordinates, a tensor of size (n_boxes, 4)
    :return: bounding boxes in boundary coordinates, a tensor of size (n_boxes, 4)
    """
    return torch.cat(
        [
            cxcy[:, :2] - (cxcy[:, 2:] / 2),  # x_min, y_min
            cxcy[:, :2] + (cxcy[:, 2:] / 2),
        ],
        1,
    )  # x_max, y_max


def cxcy_to_gcxgcy(cxcy, priors_cxcy):
    """
    Encode bounding boxes (that are in center-size form) w.r.t. the corresponding prior boxes (that are in center-size form).
    For the center coordinates, find the offset with respect to the prior box, and scale by the size of the prior box.
    For the size coordinates, scale by the size of the prior box, and convert to the log-space.
    In the model, we are predicting bounding box coordinates in this encoded form.
    :param cxcy: bounding boxes in center-size coordinates, a tensor of size (n_priors, 4)
    :param priors_cxcy: prior boxes with respect to which the encoding must be performed, a tensor of size (n_priors, 4)
    :return: encoded bounding boxes, a tensor of size (n_priors, 4)
    """

    # The 10 and 5 below are referred to as 'variances' in the original Caffe repo, completely empirical
    # They are for some sort of numerical conditioning, for 'scaling the localization gradient'
    # See https://github.com/weiliu89/caffe/issues/155
    return torch.cat(
        [
            (cxcy[:, :2] - priors_cxcy[:, :2])
            / (priors_cxcy[:, 2:] / 10),  # g_c_x, g_c_y
            torch.log(cxcy[:, 2:] / priors_cxcy[:, 2:]) * 5,
        ],
        1,
    )  # g_w, g_h


def gcxgcy_to_cxcy(gcxgcy, priors_cxcy):
    """
    Decode bounding box coordinates predicted by the model, since they are encoded in the form mentioned above.
    They are decoded into center-size coordinates.
    This is the inverse of the function above.
    :param gcxgcy: encoded bounding boxes, i.e. output of the model, a tensor of size (n_priors, 4)
    :param priors_cxcy: prior boxes with respect to which the encoding is defined, a tensor of size (n_priors, 4)
    :return: decoded bounding boxes in center-size form, a tensor of size (n_priors, 4)
    """

    return torch.cat(
        [
            gcxgcy[:, :2] * priors_cxcy[:, 2:] / 10 + priors_cxcy[:, :2],  # c_x, c_y
            torch.exp(gcxgcy[:, 2:] / 5) * priors_cxcy[:, 2:],
        ],
        1,
    )  # w, h


def find_jaccard_overlap(set_1, set_2):
    """
    Find the Jaccard Overlap (IoU) of every box combination between two sets of boxes that are in boundary coordinates.
    :param set_1: set 1, a tensor of dimensions (n1, 4)
    :param set_2: set 2, a tensor of dimensions (n2, 4)
    :return: Jaccard Overlap of each of the boxes in set 1 with respect to each of the boxes in set 2, a tensor of dimensions (n1, n2)
    """

    # Find intersections
    intersection = find_intersection(set_1, set_2)  # (n1, n2)

    # Find areas of each box in both sets
    areas_set_1 = (set_1[:, 2] - set_1[:, 0]) * (set_1[:, 3] - set_1[:, 1])  # (n1)
    areas_set_2 = (set_2[:, 2] - set_2[:, 0]) * (set_2[:, 3] - set_2[:, 1])  # (n2)

    # Find the union
    # PyTorch auto-broadcasts singleton dimensions
    union = (
        areas_set_1.unsqueeze(1) + areas_set_2.unsqueeze(0) - intersection
    )  # (n1, n2)

    return intersection / union  # (n1, n2)


def find_intersection(set_1, set_2):
    """
    Find the intersection of every box combination between two sets of boxes that are in boundary coordinates.
    :param set_1: set 1, a tensor of dimensions (n1, 4)
    :param set_2: set 2, a tensor of dimensions (n2, 4)
    :return: intersection of each of the boxes in set 1 with respect to each of the boxes in set 2, a tensor of dimensions (n1, n2)
    """

    # PyTorch auto-broadcasts singleton dimensions
    lower_bounds = torch.max(
        set_1[:, :2].unsqueeze(1), set_2[:, :2].unsqueeze(0)
    )  # (n1, n2, 2)
    upper_bounds = torch.min(
        set_1[:, 2:].unsqueeze(1), set_2[:, 2:].unsqueeze(0)
    )  # (n1, n2, 2)
    intersection_dims = torch.clamp(upper_bounds - lower_bounds, min=0)  # (n1, n2, 2)
    return intersection_dims[:, :, 0] * intersection_dims[:, :, 1]  # (n1, n2)


def decimate(tensor, m):
    """
    Decimate a tensor by a factor 'm', i.e. downsample by keeping every 'm'th value.
    This is used when we convert FC layers to equivalent Convolutional layers, BUT of a smaller size.
    :param tensor: tensor to be decimated
    :param m: list of decimation factors for each dimension of the tensor; None if not to be decimated along a dimension
    :return: decimated tensor
    """
    assert tensor.dim() == len(m)
    for d in range(tensor.dim()):
        if m[d] is not None:
            tensor = tensor.index_select(
                dim=d, index=torch.arange(start=0, end=tensor.size(d), step=m[d]).long()
            )

    return tensor


def clip_box(box, width, height):
    """
    Clipping of box for image.
    :param box: torch.Tensor with shape(num_boxes, 4)
    :param width : int
    :param height : ing
    """
    if isinstance(box, np.ndarray):
        raise NotImplementedError("Boxes must be torch.Tensor")
    box[:, 0], box[:, 2] = torch.clamp(box[:, 0], min=0, max=width), torch.clamp(
        box[:, 2], min=0, max=width
    )
    box[:, 1], box[:, 3] = torch.clamp(box[:, 1], min=0, max=height), torch.clamp(
        box[:, 3], min=0, max=height
    )
    return box


def keypoints2box(keypoints):
    """
    Keypoints to box function
    :param keypoint : must be torch.Tensor with shape(num_keypoints, 2)
    """
    keypoints = keypoints.reshape(-1, 2)
    if isinstance(keypoints, np.ndarray):
        keypoints = torch.as_tensor(keypoints)
    xmin, xmax = torch.min(keypoints[:, 0]), torch.max(keypoints[:, 0])
    ymin, ymax = torch.min(keypoints[:, 1]), torch.max(keypoints[:, 1])
    return torch.Tensor([xmin, ymin, xmax, ymax])


def box2percent(box):
    pass


def keypoints2percent(keypoints):
    pass
