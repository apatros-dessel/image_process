# -*- coding: utf-8 -*-

# RasterData and MultiRasterData

import gdal

class RasterData:

    def __init__(self, path2raster, data=0):
        raster_ds = gdal.Open(path2raster)
        if raster_ds is None:
            print('Raster dataset not found by path: {}, cannot create raster iterator'.format(path2raster))
            del self
        else:
            self.path = path2raster
            self.ds = raster_ds
            self.data = data
            self.len = raster_ds.RasterCount
            self.bandnums = list(range(1, self.len + 1))
            self.id = 0

    def __len__(self):
        return self.len

    def __iter__(self):
        self.id = 0
        return self

    def __next__(self):
        if self.id < self.len:
            band_id = self.bandnums[self.id]
            self.id += 1
            return self.getget(band_id)
        else:
            raise StopIteration

    def next(self):
        return self.__next__()

    def getget(self, band_id):
        if isinstance(self.data, (tuple, list)):
            export = []
            for data_id in self.data:
                export.append(self.get(band_id, data_id))
            return tuple(export)
        else:
            return self.get(band_id, self.data)

    def get(self, band_id, data):
        if data == 0:
            return band_id
        elif data == 1:
            return self.ds.GetRasterBand(band_id)
        elif data == 2:
            return self.ds.GetRasterBand(band_id).ReadAsArray()
        elif data == 3:
            return self.ds.GetRasterBand(band_id).DataType
        elif data == 4:
            return self.ds.GetRasterBand(band_id).GetNoDataValue()
        else:
            print('Incorrect data: {}'.format(data))
            return None

    def restart(self):
        self.id = 0

    def __getitem__(self, item):
        return self.getget(self.bandnums[item])

    def getting(self, data, band_order = None):
        copy = RasterData(self.path, data)
        if band_order is None:
            band_order = self.bandnums
        copy.setbands(band_order)
        return copy

    def setbands(self, band_order = [1,2,3]):
        for i in range(len(band_order)-1, -1, -1):
            band_order[i] = int(band_order[i])
            if (band_order[i] <= 0) or (band_order[i] > self.len):
                band_order.pop(i)
        self.bandnums = band_order
        self.len = len(band_order)
        return self

class MultiRasterData:

    def __init__(self, bandpaths, data=0):
        self.bandpaths = bandpaths
        self.raster_data = []
        self.data = data
        for path2raster, band_id in bandpaths:
            self.raster_data.append(RasterData(path2raster, data=data).setbands([band_id]))
        self.len = len(self.raster_data)
        self.id = 0

    def __len__(self):
        return self.len

    def __iter__(self):
        self.id = 0
        for data in self.raster_data:
            data.restart()
        return self

    def __next__(self):

        try:
            return self.raster_data[self.id].__next__()

        except StopIteration:
            self.id += 1

            if self.id >= self.len:
                raise StopIteration

            try:
                self.raster_data[self.id].restart()
                return self.raster_data[self.id].__next__()
            except:
                raise AssertionError

    def next(self):
        return self.__next__()

    def getting(self, data):
        return MultiRasterData(self.bandpaths, data=data)
