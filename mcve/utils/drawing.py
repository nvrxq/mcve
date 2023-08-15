from PIL import Image
import numpy as np
from typing import Any
import torch
from torchvision import transforms as T


def image_grid(imgs: list, rows, cols):
    """
    Credit to : https://huggingface.co/blog/controlnet
    imgs : list[Image]
    """
    assert len(imgs) == rows * cols

    w, h = imgs[0].size
    grid = Image.new("RGB", size=(cols * w, rows * h))
    grid_w, grid_h = grid.size

    for i, img in enumerate(imgs):
        grid.paste(img, box=(i % cols * w, i // cols * h))
    return grid
