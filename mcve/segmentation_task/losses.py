import torch.nn.functional as F


def iou_loss(inputs, targets, smooth=1):
    inputs = F.sigmoid(inputs)

    # flatten label and prediction tensors
    inputs = inputs.view(-1)
    targets = targets.view(-1)

    # intersection is equivalent to True Positive count
    # union is the mutually inclusive area of all labels & predictions
    intersection = (inputs * targets).sum()
    total = (inputs + targets).sum()
    union = total - intersection

    IoU = (intersection + smooth) / (union + smooth)

    return 1 - IoU


def dice(inputs, targets, smooth=1):
    inputs = F.sigmoid(inputs)

    # flatten label and prediction tensors
    inputs = inputs.view(-1)
    targets = targets.view(-1)

    intersection = (inputs * targets).sum()
    dice_loss = 1 - (2.0 * intersection + smooth) / (
        inputs.sum() + targets.sum() + smooth
    )
    BCE = F.binary_cross_entropy(inputs, targets.float(), reduction="mean")
    Dice_BCE = BCE + dice_loss
