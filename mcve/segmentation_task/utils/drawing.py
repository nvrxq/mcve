import numpy as np
import matplotlib.pyplot as plt


def visualize_seg_mask(image: np.ndarray, mask: np.ndarray, color=[0, 255, 0]):
    """
    Args:
    :img - numpy image
    :mask - binary mask
    :color - RGB code color
    """
    color_seg = np.zeros((mask.shape[0], mask.shape[1], 3), dtype=np.uint8)
    color_seg[mask == 1, :] = color
    color_seg = color_seg[..., ::-1]  # convert to BGR

    img = (
        np.array(image) * 0.5 + color_seg * 0.5
    )  # plot the image with the segmentation map
    img = img.astype(np.uint8)

    plt.figure(figsize=(15, 10))
    plt.imshow(img)
    plt.axis("off")
    plt.show()
