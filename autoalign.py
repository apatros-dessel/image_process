# !/usr/bin/python3.7
# by Andrew Aralov
import os
import copy
import pickle
import json
import time
import cv2
import numpy as np
from sklearn import linear_model
from osgeo import gdal, gdalconst, osr, ogr
import matplotlib.pyplot as plt
import argparse
# import thinplate as tps

from common import scale_perspective, scale_linear


# dname = 'KV6_08067_06006_00_KANOPUS_20200610_083843_083913'
# name1 = 'images/KV6_08067_06006_00_KANOPUS_20200610_083843_083913.SCN1.PMS.L2'
# name2 = 'images/KV6_08067_06006_00_KANOPUS_20200610_083843_083913.SCN2.PMS.L2'

# dname = 'KV1_39373_30574_03_KANOPUS_20190827_091843_092013'
# name1 = 'images/KV1_39373_30574_03_KANOPUS_20190827_091843_092013.SCN3.PMS.L2'
# name2 = 'images/KV1_37536_29328_01_KANOPUS_20190428_091817_091918.SCN4.PMS.L2'

# dname = 'KV1_KV6'
# name1 = 'images/KV1_39373_30574_03_KANOPUS_20190827_091843_092013.SCN2.MS.L2'
# name2 = 'images/KV6_03710_02643_01_KANOPUS_20190828_084020_084250.SCN3.MS.L2'

# dname = 'KV1_KV5'
# name1 = 'new_images/KV5_02434_01867_02_KANOPUS_20190605_080041_080113.SCN3.PMS.L2'
# name2 = 'new_images/KV1_39403_30598_02_KANOPUS_20190829_084547_084759.SCN2.PMS.L2'

# dname = 'Ganin_test'
# name1 = 'images/cropped1'
# name2 = 'images/cropped2'


def visualize(**images):
	"""PLot images in one row."""
	n = len(images)
	plt.figure(figsize=(16, 5))
	for i, (name, image) in enumerate(images.items()):
		plt.subplot(1, n, i + 1)
		plt.xticks([])
		plt.yticks([])
		plt.title(' '.join(name.split('_')).title())
		plt.imshow(image)
	plt.show()


def keypoint_copy(k):
	return cv2.KeyPoint(x = k.pt[0], y = k.pt[1],
            _size = k.size, _angle = k.angle,
            _response = k.response, _octave = k.octave,
            _class_id = k.class_id)


def distance(pt1, pt2):
	return np.sqrt((pt1[0] - pt2[0])**2 + (pt1[1] - pt2[1])**2)


def find_linear(src_pts, dst_pts):
	src_pts = np.array([[x, y, 1] for x,y in list(src_pts)])
	model = linear_model.LinearRegression(fit_intercept=False)
	model.fit(src_pts, dst_pts)
	return model.coef_


def find_perspective(src_pts, dst_pts):
	return cv2.findHomography(src_pts, dst_pts, cv2.LMEDS)[0]


def ImageProperties(ifile):
	ds = gdal.Open ( ifile, gdalconst.GA_ReadOnly )
	width = ds.RasterXSize
	height = ds.RasterYSize
	gt = ds.GetGeoTransform()
	minx = gt[0]
	miny = gt[3] + width*gt[4] + height*gt[5]
	maxx = gt[0] + width*gt[1] + height*gt[2]
	maxy = gt[3]
	template = 'POLYGON ((%(minx)f %(miny)f, %(minx)f %(maxy)f, %(maxx)f %(maxy)f, %(maxx)f %(miny)f, %(minx)f %(miny)f))'
	r1 = {'minx': minx, 'miny': miny, 'maxx': maxx, 'maxy': maxy}
	wkt = template % r1
	srs=osr.SpatialReference()
	srs.ImportFromWkt(ds.GetProjectionRef())
	return wkt, int(srs.GetAttrValue("AUTHORITY", 1)), srs, gt


def dataset2grayscale(ds):
	array = ds.GetRasterBand(1).ReadAsArray()
	return array


def serialize_keypoint(kp):
	return {'x': kp.pt[1], 'y': kp.pt[0], 'size': kp.size, 'angle': kp.angle}


def save_keypoints_as_geo_json(kps1, kps2, ds, fname):
	srs = osr.SpatialReference()
	srs.ImportFromWkt(ds.GetProjectionRef())
	gt = ds.GetGeoTransform()
	obj = {}
	obj['type'] = 'FeatureCollection'
	obj['crs'] = {
		'type': 'name',
		'properties': {'name': 'urn:ogc:def:crs:EPSG::{0}'.format(srs.GetAttrValue("AUTHORITY", 1))}
	}
	features = []
	for kp1, kp2 in zip(kps1, kps2):
		pt1 = (gt[0] + gt[1]*kp1.pt[0], gt[3] + gt[5]*kp1.pt[1])
		pt2 = (gt[0] + gt[1]*kp2.pt[0], gt[3] + gt[5]*kp2.pt[1])

		wkt = 'LINESTRING ({0} {1}, {2} {3})'.format(pt1[0], pt1[1], pt2[0], pt2[1])
		features.append({
			'type': 'Feature',
			'properties': {
				'distance': distance(kp1.pt, kp2.pt)
			},
			'geometry': json.loads(ogr.CreateGeometryFromWkt(wkt, srs).ExportToJson())
		})
	obj['features'] = features

	open(fname, 'w').write(json.dumps(obj))


def find_matches_by_detector(array1, array2,
							detector = cv2.ORB.create(nfeatures=3),
							matcher = cv2.BFMatcher.create(cv2.NORM_HAMMING, True),
							nmatches=None):

	kps1, descrs1 = detector.detectAndCompute(array1, None)
	kps2, descrs2 = detector.detectAndCompute(array2, None)

	# necessary for SIFT and SURF (maybe cv2 bug)
	if len(kps1) == 0 or len(kps2) == 0:
		matches = []
	else:
		matches = matcher.match(descrs1, descrs2)
		matches.sort(key=lambda x: x.distance)

		if nmatches is not None and nmatches < len(matches):
			matches = matches[:nmatches]

	return kps1, kps2, matches


def grid_generator(shape, batch_size, overlay):
	grid_size = (shape[0] // batch_size[0], shape[1] // batch_size[1])
	for i in range(grid_size[0]):
		for j in range(grid_size[1]):
			ly = max(batch_size[0] * i - batch_size[0] * overlay, 0)
			ry = batch_size[0] * (i+1)

			lx = max(batch_size[1] * j - batch_size[1] * overlay, 0)
			rx = batch_size[1] * (j+1)

			ly, ry, lx, rx = map(int, [ly, ry, lx, rx])

			yield ly, ry, lx, rx


def find_points_by_grid_detector(array1, array2, batch_size, overlay,
								 detector = cv2.ORB.create(nfeatures=3),
								 matcher = cv2.BFMatcher.create(cv2.NORM_HAMMING, True),
								 nmatches=None):

	kps1 = []
	kps2 = []
	matches = []

	for ly, ry, lx, rx in grid_generator(array1.shape, batch_size, overlay):
		batch1 = array1[ly : ry, lx : rx]
		batch2 = array2[ly : ry, lx : rx]

		# empty batch
		if np.sum(batch1 * batch2) == 0:
			continue

		bkps1, bkps2, bmatches = find_matches_by_detector(batch1, batch2, detector, matcher, nmatches)

		for bmatch in bmatches:
			kp1 = bkps1[bmatch.queryIdx]
			kp2 = bkps2[bmatch.trainIdx]

			kp1g = keypoint_copy(kp1)
			kp1g.pt = (kp1.pt[0] + lx, kp1.pt[1] + ly)
			kp2g = keypoint_copy(kp2)
			kp2g.pt = (kp2.pt[0] + lx, kp2.pt[1] + ly)
			kps1.append(kp1g)
			kps2.append(kp2g)
			matches.append(cv2.DMatch(len(kps1) - 1, len(kps2) - 1, bmatch.distance))

			# img = cv2.drawMatches(batch1, bkps1, batch2, bkps2, bmatches, None, 255)
			# plt.imshow(img)
			# plt.show()
			# if draw_matches:
			# 	img = cv2.drawMatches(batch1, bkps1, batch2, bkps2, bmatches, None, flags=2)
			# 	plt.imshow(img)
			# 	plt.show()

			# cv2.imwrite(os.path.join('examples', 'KV1_39373_30574_03_KANOPUS_20190827_091843_092013', 'SURF',
			# 						 f'{ly}-{ry}_{lx}-{rx}.png'), img)

	return kps1, kps2, matches


def get_dist_distr(kps1, kps2, matches):
	accuracy = []

	for match in matches:
		kp1 = kps1[match.queryIdx]
		kp2 = kps2[match.trainIdx]

		accuracy.append(distance(kp1.pt, kp2.pt))

	return accuracy


def show_stat(kps1, kps2, matches, shape):
	accuracy = get_dist_distr(kps1, kps2, matches)

	print('Points count:', len(kps1))
	print('Average distance:', np.mean(accuracy))
	print('Variance:', np.var(accuracy))

	if args.plot_stat:
		dx = []
		dy = []
		for match in matches:
			kp1 = kps1[match.queryIdx]
			kp2 = kps2[match.trainIdx]

			dy.append(kp1.pt[0] - kp2.pt[0])
			dx.append(kp1.pt[1] - kp2.pt[1])

		pmap = np.zeros((shape[0], shape[1], 3), np.uint8)
		angle_scale = 240 / max([abs((kp1.angle - kp2.angle) % 360) for kp1, kp2 in zip(kps1, kps2)])
		for kp1, kp2 in zip(kps1, kps2):
			dst = distance(kp1.pt, kp2.pt)
			dangle = angle_scale * abs(kp1.angle - kp2.angle)
			cv2.circle(pmap, tuple(map(int, kp1.pt)), int(dst), (dangle, dangle, dangle), -1)

		plt.figure(figsize=(16,5))
		plt.subplot(1, 3, 1)
		plt.hist(accuracy, bins=range(0, 250, 5))
		plt.ylim(top=1000)

		plt.subplot(1, 3, 2)
		plt.axhline(color='black')
		plt.axvline(color='black')
		plt.plot(dx, dy, 'o')

		plt.subplot(1, 3, 3)
		plt.imshow(pmap)
		plt.show()


def exclude_range_distance(kps1, kps2, matches, min, max):
	nkps1, nkps2, nmatches = [], [], []
	for match in matches:
		kp1 = kps1[match.queryIdx]
		kp2 = kps2[match.trainIdx]

		dst = distance(kp1.pt, kp2.pt)
		if not (min <= dst <= max):
			nkps1.append(kp1)
			nkps2.append(kp2)
			nmatches.append(cv2.DMatch(len(nkps1) - 1, len(nkps2) - 1, match.distance))

	return nkps1, nkps2, nmatches


def exclude_range_count(kps1, kps2, matches, min, bsize, exclude_first):
	accuracy = get_dist_distr(kps1, kps2, matches)
	accuracy_hist, _ = np.histogram(accuracy, bins=range(0, int(max(accuracy))+bsize+1, bsize))
	accuracy_hist[accuracy_hist < min] = 0
	nkps1, nkps2, nmatches = [], [], []

	for match in matches:
		kp1 = kps1[match.queryIdx]
		kp2 = kps2[match.trainIdx]

		dst = distance(kp1.pt, kp2.pt)
		if (accuracy_hist[int(np.floor(dst / bsize))] != 0) and (not exclude_first or dst >= bsize):
			nkps1.append(kp1)
			nkps2.append(kp2)
			nmatches.append(cv2.DMatch(len(nkps1) - 1, len(nkps2) - 1, match.distance))


	return nkps1, nkps2, nmatches


def exclude_angles(kps1, kps2, matches, max):
	nkps1, nkps2, nmatches = [], [], []
	for match in matches:
		kp1 = kps1[match.queryIdx]
		kp2 = kps2[match.trainIdx]

		if (kp2.angle - 10)%360 <= kp1.angle <= (kp2.angle + 10)%360:
			nkps1.append(kp1)
			nkps2.append(kp2)
			nmatches.append(cv2.DMatch(len(nkps1) - 1, len(nkps2) - 1, match.distance))

	return nkps1, nkps2, nmatches


def smart_exclude(kps1, kps2, matches, bsize, exclude_first):
	kps1, kps2, matches = exclude_angles(kps1, kps2, matches, 20)
	kps1, kps2, matches = exclude_range_count(kps1, kps2, matches, 0.015 * len(matches), bsize, exclude_first)
	kps1, kps2, matches = exclude_range_distance(kps1, kps2, matches, 75, np.inf)

	return kps1, kps2, matches


def process(array1, array2, bsize, exclude_first, finder, ds):
	kps1, kps2, matches = find_points_by_grid_detector(array1, array2, (90 * 2, 90 * 2), 0.5,
													   cv2.xfeatures2d.SURF_create(),
													   cv2.BFMatcher_create(cv2.NORM_L2, True), 7)
	process.counter += 1
	t = os.path.splitext(args.transform_path)[0]

	if args.print_stat:
		show_stat(kps1, kps2, matches, array1.shape)
		save_keypoints_as_geo_json(kps1, kps2, ds, '{0}_keypoints{1}.json'.format(t, process.counter))

	kps1, kps2, matches = smart_exclude(kps1, kps2, matches, bsize, exclude_first)

	if args.print_stat:
		show_stat(kps1, kps2, matches, array1.shape)
		save_keypoints_as_geo_json(kps1, kps2, ds, '{0}_keypoints{1}_excluded.json'.format(t, process.counter))

	src_pts = np.array([kp.pt for kp in kps1], np.float)
	dst_pts = np.array([kp.pt for kp in kps2], np.float)

	mn = np.mean(get_dist_distr(kps1, kps2, matches))
	if mn >= 40:
		raise RuntimeError('Keypoints avarage distance is too large: ' + str(mn))
	elif len(src_pts) < 20:
		raise RuntimeError('Not enough keypoints are found: ' + str(len(src_pts)))
	else:
		H = finder(src_pts, dst_pts)

	# open(os.path.join('examples', dname, 'full', 'kps1.json'), 'w').write(json.dumps(kps1, default=serialize_keypoint, indent=4))
	# open(os.path.join('examples', dname, 'full', 'kps2.json'), 'w').write(json.dumps(kps2, default=serialize_keypoint, indent=4))

	return H


parser = argparse.ArgumentParser(description='Given 2 geotiff images finds transformation between')
parser.add_argument('-d', action='store_true', dest='print_stat', help='Print stat')
parser.add_argument('-p', action='store_true', dest='plot_stat', help='Plot stat')
parser.add_argument('-i', default=None, dest='inter_dir', help='Directory to save intermediate images')
parser.add_argument('-t', default='/tmp/geoaligner', dest='temp_dir', help='Temporary directory')
parser.add_argument('-l', action='store_true', dest='linear', help='Find only linear transformation')
parser.add_argument('-c', default=None, dest='composit_path', help='Create composit in the specified path')
parser.add_argument('img1_path', help='First filename (this one is transformed)')
parser.add_argument('img2_path', help='Second filename (this is the reference)')
parser.add_argument('transform_path', help='Filename for transformation info (could be used with warp.py)')

args = parser.parse_args()

process.counter = 0
if args.linear:
	warper = cv2.warpAffine
	finder = find_linear
	scaler = scale_linear
else:
	warper = cv2.warpPerspective
	finder = find_perspective
	scaler = scale_perspective

if not os.path.exists(args.temp_dir):
	os.mkdir(args.temp_dir)

start = time.time()
print("arg", args.img2_path)
# GDAL based intersection
imI_wkt, imI_epsg, imI_srs, imI_gt = ImageProperties(args.img1_path)
imF_wkt, imF_epsg, imF_srs, imF_gt = ImageProperties(args.img2_path)
imI_geom = ogr.CreateGeometryFromWkt(imI_wkt, imI_srs)
imF_geom = ogr.CreateGeometryFromWkt(imF_wkt, imF_srs)

if imI_epsg != imF_epsg:
	imF_geom.TransformTo(imI_srs)

intersection_geom = imF_geom.Intersection(imI_geom)
ulx, lrx, lry, uly = intersection_geom.GetEnvelope()
bbox = [str(ulx), str(uly), str(lrx), str(lry)]

cmd = 'gdal_translate -of VRT -projwin {0} "{1}" "{2}"'.format(' '.join(bbox), args.img1_path, os.path.join(args.temp_dir, '1.tif'))
os.system(cmd)
cmd = 'gdal_translate -of VRT -projwin {0} "{1}" "{2}"'.format(' '.join(bbox), args.img2_path, os.path.join(args.temp_dir, '2.tif'))
os.system(cmd)

im1_ds = gdal.Open(os.path.join(args.temp_dir, '1.tif'))
im2_ds = gdal.Open(os.path.join(args.temp_dir, '2.tif'))

array1 = dataset2grayscale(im1_ds)
array2 = dataset2grayscale(im2_ds)

array2 = cv2.resize(array2, (array1.shape[1], array1.shape[0]), interpolation=cv2.INTER_AREA)

cv2.normalize(array1, array1, 0, 255, cv2.NORM_MINMAX)
cv2.normalize(array2, array2, 0, 255, cv2.NORM_MINMAX)

array1 = array1.astype(np.uint8)
array2 = array2.astype(np.uint8)

res = copy.deepcopy(array1)
Hs = []
n = 1 + (not args.linear)
for i in range(n):
	H = process(res, array2, n-i, i == 0, finder, im1_ds)
	Hs.append(H)
	res = warper(res, H, (res.shape[1], res.shape[0]))

# def warp_image_cv(img, c_src, c_dst, dshape=None):
# 	dshape = dshape or img.shape
# 	theta = tps.tps_theta_from_points(c_src, c_dst, reduced=True)
# 	grid = tps.tps_grid(theta, c_dst, dshape)
# 	mapx, mapy = tps.tps_grid_to_remap(grid, img.shape)
# 	return cv2.remap(img, mapx, mapy, cv2.INTER_CUBIC)
#
# res = warp_image_cv(array1, np.array([[0, 0], [1, 1], [5,3], [100, 1]]), np.array([[0,0], [1,1], [3,3], [101, 4]]))
# res = warp_image_cv(array1, src_pts, dst_pts)

# resrgb = warp_image_cv(array1rgb, src_pts, dst_pts)

if args.composit_path is not None:
	ngt = np.array(imF_gt)
	ngt[0] = ulx
	ngt[3] = uly

	res_ds = gdal.GetDriverByName('GTiff').Create(args.composit_path, res.shape[1], res.shape[0], im1_ds.RasterCount*2, gdalconst.GDT_UInt16)
	res_ds.SetGeoTransform(tuple(ngt))
	srs = imF_srs
	res_ds.SetProjection(srs.ExportToWkt())

	for i, img in enumerate([im1_ds, im2_ds]):
		for j in range(1, img.RasterCount+1):
			band = img.GetRasterBand(j).ReadAsArray()
			if i == 0:
				for H in Hs:
					band = warper(band, H, (band.shape[1], band.shape[0]), flags=cv2.INTER_NEAREST)
			res_ds.GetRasterBand(img.RasterCount*i + j).WriteArray(band)

	mask = np.ones((im1_ds.RasterYSize, im1_ds.RasterXSize), dtype=np.uint)
	for i in range(1, res_ds.RasterCount + 1):
		arr = res_ds.GetRasterBand(i).ReadAsArray()
		mask[arr == 0] = 0

	for i in range(1, res_ds.RasterCount + 1):
		arr = res_ds.GetRasterBand(i).ReadAsArray()
		arr[mask == 0] = 0
		res_ds.GetRasterBand(i).WriteArray(arr)
		res_ds.GetRasterBand(i).SetNoDataValue(0)

	res_ds.FlushCache()


transform = [Hs, intersection_geom, im1_ds.GetGeoTransform()]
open(args.transform_path, 'wb').write(pickle.dumps(transform))

if args.print_stat:
	print('Elapsed time:', time.time() - start)

if args.inter_dir is not None:
	cv2.imwrite(os.path.join(args.inter_dir, 'sum_before.png'), array1 + array2)
	cv2.imwrite(os.path.join(args.inter_dir, 'sum_after.png'), res+array2)
	cv2.imwrite(os.path.join(args.inter_dir, 'array1.png'), array1)
	cv2.imwrite(os.path.join(args.inter_dir, 'array2.png'), array2)
	cv2.imwrite(os.path.join(args.inter_dir, 'res.png'), res)
