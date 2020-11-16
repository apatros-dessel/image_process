# by Andrew Aralov

import numpy as np


def scale_perspective(H, s):
	H[0:2, 2] /= s
	H[2, 0:2] *= s


def scale_linear(H, s):
	H[0:2, 2] *= s


def offset_linear(H, f):
	H[0, 2] -= f[0]*H[0,0] + f[1]*H[0,1] - f[0]
	H[1, 2] -= f[0]*H[1,0] + f[1]*H[1,1] - f[1]

