from image_processor import *

path = r'f:\102_2020_949'

proc = process().input(path)

scroll(proc.get_ids())

for ascene in proc.scenes:
    # print(ascene.get_band_path('red'))
    # Image.open(ascene.get_raster_path('image')).show()
    # print(ascene.datamask())
    pass

proc.GetCoverJSON(fullpath(path, 'KAN_cover.json'))
