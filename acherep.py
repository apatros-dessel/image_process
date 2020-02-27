# My adaptation of change detection code by Alexander Cherepanov

from image_processor import *

def ImageMetadata(filename):
    metadata={'date':'','year':'','month':'','day':'','ps':'','sensor':'','numbands':''}
    temp=filename.split('_')
    metadata['date']=temp[0]
    metadata['year']=metadata['date'][:4]
    metadata['month']=metadata['date'][4:6]
    metadata['day']=metadata['date'][6:]
    metadata['ps']=temp[1]
    metadata['sensor']=temp[2]
    metadata['numbands']=temp[3].replace('b','')
    return metadata

def ForestMask(path2red, path2nir, image_metadata, red=[100, 500], nir=[1000, 3100], threshold = 60, min_pixel_num = 6, output_shapefile=None, output_cirfile=None, compress = 'NONE', GaussianBlur=True):

    # image_ds = geodata.gdal.Open(path2image)
    band_data_red = geodata.get_band_array(path2red)
    band_data_nir = geodata.get_band_array(path2nir)

    assert band_data_nir.shape==band_data_red.shape

    if (band_data_red is not None) and (band_data_nir is not None):

            # fieldnames = ["DATA", "SENSOR", "IMG_FILE", "AREA"]
            # fields = {"DATA":('string',8), "SENSOR":('string',5), "IMG_FILE":('string',64), "AREA":('float',6,2)}
            # fields_value = {"DATA":image_metadata['date'], "SENSOR":image_metadata['sensor'], "IMG_FILE": path2red, "AREA":None}

            forest_mask = np.ones(band_data_red.shape, dtype=np.int8)

            forest_mask[band_data_nir<nir[0]]=0
            forest_mask[band_data_nir>nir[1]]=0
            forest_mask[band_data_red<red[0]]=0
            forest_mask[band_data_red>red[1]]=0

            forest_mask[forest_mask==1]=255

            if GaussianBlur:
                forest_mask = geodata.cv2.GaussianBlur(forest_mask.astype(np.uint8),(5,5),0)

            forest_mask[forest_mask<threshold]=0
            forest_mask[forest_mask>=threshold]=255

            if output_cirfile is None:
                output_cirfile = tempname('tif')

            cir_image_ds = geodata.ds(output_cirfile, copypath=path2red[0], options={'bandnum': 3, 'compress': compress})

            cir_image_ds.GetRasterBand(1).WriteArray(band_data_nir)
            cir_image_ds.GetRasterBand(2).WriteArray(band_data_red)
            cir_image_ds.GetRasterBand(3).WriteArray(forest_mask)


            # min_area = min_pixel_num * image_ds.GetGeoTransform()[1] * image_ds.GetGeoTransform()[1]
            min_area = min_pixel_num * cir_image_ds.GetGeoTransform()[1] * cir_image_ds.GetGeoTransform()[5]

            cir_image_ds = None

            # vector_lib.Raster2VectorP(image_ds, forest_mask, output_shapefile+'_p.shp', fieldnames, fields, fields_value, min_area)
            # vector_lib.Raster2VectorM(image_ds, forest_mask, output_shapefile+'_m.shp', fieldnames, fields, fields_value, min_area)

            if output_shapefile is None:
                output_shapefile = tempname('shp')

            ds_out = geodata.save_to_shp(output_cirfile, output_shapefile, band_num=3, classify_table=[(60, None, 255)])

            ds_out, lyr_out = geodata.get_lyr_by_path(output_shapefile, 1)

            del_list = []
            for feat in lyr_out:
                if feat.GetGeometryRef().GetArea() < min_area:
                    del_list.append(feat.GetFID())

            for FID in del_list:
                lyr_out.DeleteFeature(FID)

            ds_out = None

            if os.path.exists(output_cirfile) and os.path.exists(output_shapefile):
                return {'status':'OK', 'shp':output_shapefile, 'cir_img':output_cirfile}
            else:
                return {'status':'ERROR', 'shp':'', 'cir_img':''}

    else:
        return {'status':'ERROR', 'shp':'', 'cir_img':''}

def BurnedMask(bandpath_green, bandpath_red, bandpath_nir, bandpath_swir1, bandpath_swir2, image_metadata,
               index_value, min_pix_num=6, output_raster=None, output_shapefile=None, output_UFC=None, output_FAR=None,
               GaussianBlur = True, compress=None):

    np.seterr(divide='ignore', invalid='ignore')
    # image_ds=gdal.Open ( input_image, GA_ReadOnly )

    if not any((bandpath_green, bandpath_red, bandpath_nir, bandpath_swir1, bandpath_swir2)) is None:

            # image_metadata=ImageMetadata(file_name)

            # if image_metadata['sensor'] in ['L5','L7','L8']:

                # if output_shapefile=='':output_shapefile=os.path.join(dir_name, file_name+'_burned_mask.SHP')
                # if output_imagefile=='':output_imagefile=os.path.join(dir_name, file_name+'_%s.TIF')
                # fieldnames=["DATA", "SENSOR", "IMG_FILE", "AREA"]
                # fields={"DATA":('string',8), "SENSOR":('string',5), "IMG_FILE":('string',64), "AREA":('float',6,2)}
                # fields_value={"DATA":image_metadata['date'], "SENSOR":image_metadata['sensor'], "IMG_FILE":input_image, "AREA":None}

                band_data_green=geodata.get_band_array(bandpath_green)
                band_data_red=geodata.get_band_array(bandpath_red)
                band_data_swir1=geodata.get_band_array(bandpath_swir1)
                band_data_nir=geodata.get_band_array(bandpath_nir)
                band_data_swir2=geodata.get_band_array(bandpath_swir2)

                nbr1=band_data_nir-band_data_swir2
                nbr2=band_data_nir+band_data_swir2

                indxZeros=np.where(nbr2==0)
                indxNonZeros=np.where(nbr2!=0)
                nbr=np.empty(nbr2.shape)
                nbr[indxZeros]=0
                nbr[indxNonZeros]=nbr1[indxNonZeros]/nbr2[indxNonZeros]
                indxZeros=np.where(nbr>=index_value)
                indxNonZeros=np.where(nbr<index_value)
                nbr[indxZeros]=0
                nbr[indxNonZeros]=255
                indxZeros=np.where(nbr2==0)

                if GaussianBlur:
                    nbr = geodata.cv2.GaussianBlur(nbr.astype(np.uint8),(5,5),0)

                nbr[nbr<60]=0
                nbr[nbr>=60]=255
                indxZeros=np.where(band_data_green==0)
                nbr[indxZeros]=0
                indxZeros=np.where(band_data_red==0)
                nbr[indxZeros]=0

                if output_UFC is None:
                    output_UFC = tempname('tif')

                if output_FAR is None:
                    output_FAR = tempname('tif')

                output_ds = geodata.ds(output_raster, copypath=bandpath_red[0], options={'bandnum': 1, 'compress': compress}, editable=True)
                output_ds.GetRasterBand(1).WriteArray(nbr)
                min_area = min_pix_num * output_ds.GetGeoTransform()[1] * output_ds.GetGeoTransform()[5]
                output_ds = None

                geodata.raster2raster((bandpath_swir2, bandpath_swir1, bandpath_red), output_UFC, compress=compress)
                geodata.raster2raster((bandpath_swir1, bandpath_nir, bandpath_green), output_FAR, compress=compress)

                if output_shapefile is not None:
                    geodata.save_to_shp(output_raster, output_shapefile, classify_table=[(60, None, 255)])

                # image753_ds = gdal.GetDriverByName("GTiff").Create( output_imagefile % ('753') , image_ds.RasterXSize, image_ds.RasterYSize,  3, GDT_UInt16)
                # image542_ds = gdal.GetDriverByName("GTiff").Create( output_imagefile % ('542') , image_ds.RasterXSize, image_ds.RasterYSize,  3, GDT_UInt16)
                # image753_ds.SetGeoTransform( image_ds.GetGeoTransform() )
                # image753_ds.SetProjection( image_ds.GetProjection() )
                # image753_ds.GetRasterBand(1).WriteArray(band_data_swir2.astype(np.int16))
                # image753_ds.GetRasterBand(2).WriteArray(band_data_swir1.astype(np.int16))
                # image753_ds.GetRasterBand(3).WriteArray(band_data_red.astype(np.int16))
                # image753_ds=None
                # image542_ds.SetGeoTransform( image_ds.GetGeoTransform() )
                # image542_ds.SetProjection( image_ds.GetProjection() )
                # image542_ds.GetRasterBand(1).WriteArray(band_data_swir1.astype(np.int16))
                # image542_ds.GetRasterBand(2).WriteArray(band_data_nir.astype(np.int16))
                # image542_ds.GetRasterBand(3).WriteArray(band_data_green.astype(np.int16))
                # image542_ds=None

                # vector_lib.Raster2VectorP(image_ds, nbr, output_shapefile+'_p.shp', fieldnames, fields, fields_value, min_area)
                # vector_lib.Raster2VectorM(image_ds, nbr, output_shapefile+'_m.shp', fieldnames, fields, fields_value, min_area)

                # if os.path.exists(output_shapefile):
                    # return {'status':'OK', 'shp':output_shapefile}
                # else:
                    # return {'status':'ERROR', 'shp':''}
    else:
        return {'status':'ERROR', 'shp':''}