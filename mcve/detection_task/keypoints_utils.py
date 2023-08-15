import numpy as np


def read_pts(filename):
    return np.loadtxt(filename, comments=("version:", "n_points:", "{", "}"))
