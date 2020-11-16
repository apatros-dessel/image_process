#!/usr/bin/python3.7
# by Andrew Aralov

import os
import pickle
import cv2
import numpy as np
from osgeo import gdal, gdalconst, osr, ogr
import matplotlib.pyplot as plt
import argparse

from common import scale_perspective, scale_linear, offset_linear


parser = argparse.ArgumentParser(description='Applies transformation found by autoalign.py')
parser.add_argument('-t', default='/tmp/geoaligner', dest='temp_dir', help='Temporary directory')
parser.add_argument('imname', help='Image filename')
parser.add_argument('transform_path', help='Transformation info filename')
parser.add_argument('result', help='Transformed image filename')

args = parser.parse_args()
imname = args.imname
transform_path = args.transform_path
resname = args.result
temp_dir = args.temp_dir

Hs, geom, tgt = pickle.loads(open(transform_path, 'rb').read())
if len(Hs) == 1 and len(Hs[0].shape) == 2:
	warper = cv2.warpAffine
	scaler = scale_linear
else:
	warper = cv2.warpPerspective
	scaler = scale_perspective

img_ds = gdal.Open(imname)
n = img_ds.RasterCount
gt = img_ds.GetGeoTransform()
s = tgt[1] / gt[1]

for H in Hs:
	scaler(H,s)

# CHECK THIS LATER!!!
f = ((gt[0] - tgt[0])/gt[1], (gt[3] - tgt[3])/gt[5])
for H in Hs:
	offset_linear(H, f)

options = ['COMPRESS=DEFLATE', 'PREDICTOR=2', 'ZLEVEL=9', 'NUM_THREADS=ALL_CPUS']

res_ds = gdal.GetDriverByName('GTiff').Create(resname, img_ds.RasterXSize, img_ds.RasterYSize, n, gdalconst.GDT_UInt16, options=options)
for i in range(1, n+1):
	band = img_ds.GetRasterBand(i)
	res = band.ReadAsArray()
	for H in Hs:
		res = warper(res, H, (res.shape[1], res.shape[0]), flags=cv2.INTER_AREA)
	res_ds.GetRasterBand(i).WriteArray(res)
	res_ds.GetRasterBand(i).SetNoDataValue(0)


res_ds.SetGeoTransform(gt)
res_ds.SetProjection(img_ds.GetProjectionRef())
res_ds.FlushCache()