from geodata import *
from image_processor import process, scene, metalib, template_dict

path_in = r''
vector_in = r''

def CreateScene(path, imsys_list = None):
    name = os.path.split(path)[1]
    templates = globals()['template_dict']
    if imsys_list is None:
        imsys_list = templates.keys()
    for imsys in imsys_list:
        tmpts = templates.get(imsys, False)
        if tmpts:
            for tmpt in tmpts:
                if re.search(tmpt, name):
                    return scene(path)

def FilteredData(folder, imsys_list = None, type = None, area = None, area_key = None, area_vals = None):
    proc = process()
    if area is not None:
        if area_key and area_vals:
            temp_area = filter_dataset_by_col(area, area_key, area_vals)
            din, lin = get_lyr_by_path(temp_area)
        else:
            temp_area = False
            din, lin = get_lyr_by_path(area)
        if lin:
            reference = lin.GetSpatialRef()
            if a
    for patch in os.walk():
        append = folder[0]
        for name in patch[2]:
            newscene = CreateScene(r'%s\%s\%s' % (folder, append, name), imsys_list = imsys_list)
            if newscene is not None:
                if type is not None:
                    if newscene.meta.type != type:
                        continue
                if lin:
                    center_geom = VectorCentroid(path, reference = reference)
                    if center_geom:
                        if not lin.Intersects(center_geom):
                            continue
                    else:
                        continue
                proc.scenes.append(newscene)
                proc.ids.append(newscene.meta.id)
    if area and temp_area:
        delete(temp_area)

din, lin = get_lyr_by_path(vector_in)

