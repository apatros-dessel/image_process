import image_processor
from geodata import *

fields_dict = OrderedDict()
fields_dict['id'] =         {'type_id': 4}
fields_dict['id_s'] =       {'type_id': 4}
fields_dict['id_neuro'] =   {'type_id': 4}
fields_dict['datetime'] =   {'type_id': 4}
fields_dict['clouds'] =     {'type_id': 2}
fields_dict['sun_elev'] =   {'type_id': 2}
fields_dict['sun_azim'] =   {'type_id': 2}
fields_dict['sat_id'] =     {'type_id': 4}
fields_dict['sat_view'] =   {'type_id': 2}
fields_dict['sat_azim'] =   {'type_id': 2}
fields_dict['channels'] =   {'type_id': 0}
fields_dict['type'] =       {'type_id': 4}
fields_dict['format'] =     {'type_id': 4}
fields_dict['rows'] =       {'type_id': 0}
fields_dict['cols'] =       {'type_id': 0}
fields_dict['epsg_dat'] =   {'type_id': 0}
fields_dict['u_size'] =  {'type_id': 0}
fields_dict['x_size'] =     {'type_id': 2}
fields_dict['y_size'] =     {'type_id': 2}
fields_dict['level'] =      {'type_id': 4}
fields_dict['area'] =       {'type_id': 2}

translator = OrderedDict()
translator['id'] =          ['product_id']
translator['datetime'] =    ['date', 'acquired']
translator['clouds'] =      ['cloud_cove']
translator['sat_id'] =      ['sat', 'satellite_']
translator['sat_elev'] =    []
translator['channels'] =    ['numb']
translator['type'] =        ['prodT']
translator['rows'] =        ['row']
translator['cols'] =        ['col', 'columns']
translator['x_size'] =      ['pixel_reso']
translator['y_size'] =      ['pixel_reso']
translator['level'] =       ['prodL']
translator['area'] =        ['area_sqkm']

path_in_list = [
    r'e:\test\cover_tver_planet_fin.json',
    # r'e:\test\cover_krym_fin.json',
    # r'e:\test\cover_samara_fin.json',
    # r'd:\digital_earth\resurs-p_new\krym\report_102_2020_108_rp.geojson',
    # r'D:/resurs_p+/ETRIS.RP1.GTNL1.4949.5.0.2014-05-14.L0.NTSOMZ_MSK.NTSOMZ_MSK.json',
]

path_out_list = [
    r'e:\test\Tver_Planet_cover.json',
    # r'e:\test\Krym_Kanopus_cover.json',
    # r'e:\test\Samara_Kanopus_cover.json',
    # r'e:\test\Krym_Resurs_cover.json',
    # r'e:\test\ETRIS.RP1.GTNL1.4949.5.0.2014-05-14.L0.NTSOMZ_MSK.NTSOMZ_MSK.json',
]

path_data_list = [
    r'\\TT-NAS-ARCHIVE\NAS-Archive-2TB-12\Planet\Tver',
    # r'd:\digital_earth\kanopus_new\krym',
    # r'd:\digital_earth\kanopus_new\samara',
    # r'd:\digital_earth\resurs-p_new\krym',
    # None
]

for path_in, path_out, path_data in zip(path_in_list, path_out_list, path_data_list):

    ds_in, lyr_in = get_lyr_by_path(path_in)
    feat_in_list = lyr_in

    json_fields(path_out, ogr.wkbMultiPolygon, 4326, fields_dict, feat_in_list, translator)

    if path_data is not None:

        proc = image_processor.process().input(path_data)
        ds_out, lyr_out = get_lyr_by_path(path_out)

        for feat in lyr_out:

            ''' For Planet '''
            ascene = proc.get_scene(feat.GetField('id')+'_3B_AnalyticMS')
            if ascene is not None:
                metadata = ascene.meta.container.get('xmltree')
                feat.SetField('id', ascene.meta.id)
                feat.SetField('id_s', ascene.meta.name('[location]'))
                feat.SetField('id_neuro', ascene.meta.name('[fullsat]-[date]-[location]-[lvl]'))
                feat.SetField('datetime', get_from_tree(metadata, 'acquisitionDateTime'))
                # feat.SetField('clouds', get_from_tree(metadata, 'acquisitionDateTime'))
                feat.SetField('sun_elev', get_from_tree(metadata, 'illuminationElevationAngle'))
                feat.SetField('sun_azim', get_from_tree(metadata, 'illuminationAzimuthAngle'))
                feat.SetField('sat_id', ascene.meta.name('[fullsat]'))
                feat.SetField('sat_view', get_from_tree(metadata, 'spaceCraftViewAngle'))
                feat.SetField('sat_azim', get_from_tree(metadata, 'azimuthAngle'))
                feat.SetField('x_size', get_from_tree(metadata, 'resolution'))
                feat.SetField('y_size', get_from_tree(metadata, 'resolution'))
                feat.SetField('epsg_dat', get_from_tree(metadata, 'epsgCode'))
                feat.SetField('u_size', 'meter')
                feat.SetField('channels', get_from_tree(metadata, 'numBands'))
                feat.SetField('level', get_from_tree(metadata, 'productType'))
                feat.SetField('format', '16U')

            ''' For Kanopus '''
            ascene = proc.get_scene(feat.GetField('id') + '.L2')
            if ascene is not None:
                metadata = ascene.meta.container.get('metadata')
                feat.SetField('id', ascene.meta.id)
                feat.SetField('id_s', ascene.meta.name('[location]'))
                feat.SetField('id_neuro', ascene.meta.name('[fullsat]-[date]-[location]-[lvl]'))
                feat.SetField('datetime', get_from_tree(metadata, 'firstLineTimeUtc'))
                feat.SetField('sun_elev', get_from_tree(metadata, 'illuminationElevationAngle'))
                feat.SetField('sun_azim', get_from_tree(metadata, 'illuminationAzimuthAngle'))
                feat.SetField('sat_id', ascene.meta.name('[fullsat]'))
                feat.SetField('sat_view', get_from_tree(metadata, 'satelliteViewAngle'))
                feat.SetField('sat_azim', get_from_tree(metadata, 'azimuthAngle'))
                feat.SetField('x_size', get_from_tree(metadata, 'productResolution'))
                feat.SetField('y_size', get_from_tree(metadata, 'productResolution'))
                feat.SetField('epsg_dat', int('326'+ re.search(r'WGS 84 / UTM zone \d+N', get_from_tree(metadata, 'wktString')).group()[18:-1]))
                feat.SetField('u_size', 'meter')
                # feat.SetField('channels', get_from_tree(metadata, 'bandCount'))
                feat.SetField('format', '16U')
                feat.SetField('level', get_from_tree(metadata, 'productType'))

            ''' For Resurs-P '''
            ascene = proc.get_scene(feat.GetField('id') + '.L2')
            if ascene is not None:
                metadata = ascene.meta.container.get('metadata')
                feat.SetField('id', ascene.meta.id)
                feat.SetField('id_s', ascene.meta.name('[location]'))
                feat.SetField('id_neuro', ascene.meta.name('[fullsat]-[date]-[location]-[lvl]'))
                feat.SetField('datetime', get_from_tree(metadata, 'firstLineTimeUtc'))
                feat.SetField('sun_elev', get_from_tree(metadata, 'illuminationElevationAngle'))
                feat.SetField('sun_azim', get_from_tree(metadata, 'illuminationAzimuthAngle'))
                feat.SetField('sat_id', ascene.meta.name('[fullsat]'))
                feat.SetField('sat_view', get_from_tree(metadata, 'satelliteViewAngle'))
                feat.SetField('sat_azim', get_from_tree(metadata, 'azimuthAngle'))
                feat.SetField('x_size', get_from_tree(metadata, 'productResolution'))
                feat.SetField('y_size', get_from_tree(metadata, 'productResolution'))
                feat.SetField('epsg_dat', int(
                    '326' + re.search(r'WGS 84 / UTM zone \d+N', get_from_tree(metadata, 'wktString')).group()[18:-1]))
                feat.SetField('u_size', 'meter')
                # feat.SetField('channels', get_from_tree(metadata, 'bandCount'))
                feat.SetField('format', '16U')
                feat.SetField('level', get_from_tree(metadata, 'productType'))

            lyr_out.SetFeature(feat)

        ds_out = None

    print('File written: {}'.format(path_out))
