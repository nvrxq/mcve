from PIL import Image, ImageDraw
import numpy as np
from typing import Any
import torch
from torchvision import transforms as T


def draw_keypoints(
    image: Any, keypoints: np.ndarray, thickness: int = 5, color: str = "red"
) -> Image:
    """
    Keypoyints Drawing Function
    Arguments:
    -------------------
    image : Pillow Image || Torch.Tensor || Numpy Array
    keypoints : Numpy array || Torch.Tensor. Shape : (num_keypoints, 2)
    width : int. Default 5.
    color : str. Default red.
    """
    if isinstance(image, np.ndarray):
        image = Image.fromarray(image)
    elif isinstance(image, torch.Tensor):
        image = T.ToPILImage()(image)
    draw = ImageDraw.Draw(image)

    for point in keypoints:
        x, y = point[0], point[1]
        draw.ellipse(
            [(x - thickness, y - thickness), (x + thickness, y + thickness)],
            outline=color,
            fill=color,
        )

    return image


def draw_bbox(image: Any, box: Any, width: int = 5, color: str = "red") -> Image:
    """
    Bounding Box Drawing Function
    Arguments:
    -----------------
    image : Pillow Image || Torch.Tensor || Numpy Array
    box : Numpy array || Torch.Tensor. Shape : (num_box, 4)
    width : int. Default 5.
    color : str. Default red.
    """
    if isinstance(image, np.ndarray):
        image = Image.fromarray(image)
    elif isinstance(image, torch.Tensor):
        image = T.ToPILImage()(image)
    print(box)
    if isinstance(box, np.ndarray):
        box = torch.as_tensor(box)
    draw = ImageDraw.Draw(image)
    box = box.reshape(-1, 4)
    for b in box:
        draw.rectangle(xy=b.tolist(), outline=color, width=5)
    return image
