from geodata import *
# gdalwarp -s_srs EPSG:4326 -t_srs EPSG:32631 -dstnodata 0.0 -tr 23.5 23.5 -r cubicspline -of GTiff -co COMPRESS=DEFLATE -co PREDICTOR=2 -co ZLEVEL=9 E:/rks/razmetka_source/resurs_kshmsa_ms_clouds/img_clouds_vr/RP1_15523_02_KSHMSA-VR_20160403_083342_083414.MS.RS.tif E:/temp/rgb2.tif
command_template = r'gdalwarp {path_in} {path_out} -s_srs EPSG:{epsg_in} -t_srs EPSG:{epsg_out} -dstnodata {nodata} -tr {pix} {pix} -r {method} -of GTiff -co COMPRESS=DEFLATE -co PREDICTOR=2 -co ZLEVEL=9 -co BIGTIFF=YES'

folder_in = r'\\172.21.195.2\thematic\!razmetka\Resurs_KSHMSA\Resurs_KSHMSA_CP\Resurs_KSHMSA_CP_surface\MS\img_check'
pixel_size = 120
# json_out = r'E:/temp/test.json'

def GetEPSG(central_lat, central_long):
    start = (6,7)[central_lat<0]
    fin = int(((central_long+180)%360)/6)
    epsg = '32%i%s' % (start, stringoflen(str(fin), 2, filler = '0', left = True))
    return epsg

def GetCommand(path_in, path_out, pixel_size = 24):
    if not os.path.exists(path_in):
        print('FILE NOT FOUND: %s' % path_in)
        return None
    raster = gdal.Open(path_in)
    srs = raster.GetSpatialRef()
    epsg_in = srs.GetAttrValue("AUTHORITY", 1)
    if epsg_in.startswith('32'):
        print('ALREADY UTM: %s' % Name(path_in))
        return None
    point = raster.GetGCPs()
    json_out = tempname('json')
    json(json_out, ds)
    dout, lout = get_lyr_by_path(json_out, 1)
    defn = lout.GetLayerDefn()
    for gcp in point:
        feat = ogr.Feature(defn)
        geom = ogr.CreateGeometryFromWkt('POINT (%f %f)' % (gcp.GCPX, gcp.GCPY))
        feat.SetGeometry(geom)
        lout.CreateFeature(feat)
    dout = None
    dout, lout = get_lyr_by_path(json_out)
    extent = lout.GetExtent()
    central_lat = ((extent[2] + extent[3]) / 2 ) % 90
    central_long = ((extent[0] + extent[1]) / 2 ) % 180
    epsg_out = GetEPSG(central_lat, central_long)
    command = command_template.format(path_in=path_in, path_out=path_out, epsg_in=epsg_in, epsg_out=epsg_out, nodata=0, pix=pixel_size, method='cubicspline')
    dout = None
    delete(json_out)
    return command.replace('&','^&')

# meta_file = folder_paths(r'e:\rks\source\Ресурс_КШМСА\KSHMSA_VR\selected_vr',1,'xml')
meta_list = {}
# for file in meta_file:
    # name = Name(file)
    # if name.endswith('.MD'):
        # meta_list[name[:-3]] = file

for path_in in folder_paths(folder_in, 1, 'tif', filter_folder=['#original_deg', '#substandard']):
    corner, name, ext = split3(path_in)
    path_out = fullpath(corner, name+'_utm', ext)
    if os.path.exists(path_out):
        print('FILE EXISTS: %s' % path_out[len(folder_in):])
    else:
        id = name.split('cut')[0].rstrip('_')
        if id in meta_list:
            meta_file = meta_list[id]
            meta = xml2tree(meta_file)
            size = get_from_tree(meta, 'productResolution')
        else:
            print('\nMETADATA NOT FOUND: %s' % id)
            size = 24
        command = GetCommand(path_in, path_out, pixel_size=pixel_size)
        # print(command)
        if command is not None:
            os.system(command)
            print('PROCESSED: %s' % path_in[len(folder_in):])
    # continue
    if os.path.exists(path_in) and os.path.exists(path_out):
        backup_folder = fullpath(corner, '#original_deg')
        suredir(backup_folder)
        rename(path_in, fullpath(backup_folder, name, ext))
        rename(path_out, path_in)
        print('RENAMED: %s' % name)