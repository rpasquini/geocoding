__author__ = 'Richard'

import geocoder
import pandas as pd
import os
import inspect
import geopandas as gpd
from shapely.geometry import Point
from pandas.io.json import json_normalize
#import xlwt

def georef(csvfilename, coordenadasderef=[-27.783613, -64.264826]):

    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

    #df3=pd.read_csv(currentdir+'\\datos geocoding para capacitacion\\'+'santiago_direcciones_prueba.csv')

    df=pd.read_csv(csvfilename)


    from itertools import islice
    json_list=[]
    for index, row in df.iterrows():
    #for index, row in islice(df.iterrows(), 4):
            print(index)

            if pd.isna(row['Barrio']):
                addressstring=str(row['Direccion'])+", "+row['Provincia']+', Argentina'
            else:
                #addressstring=str(row['Direccion'])+", BARRIO "+row['Barrio']+row['Provincia']+', Argentina'
                addressstring=str(row['Direccion'])+", "+row['Provincia']+', Argentina'


            #print(addressstring)
            g=geocoder.arcgis(addressstring, proximity=coordenadasderef)
            json_list.append(g.json)


    results=json_normalize(json_list)

    dffinal=pd.concat([df, results], axis=1)

    dffinal.to_excel('resultados_geo.xls')

    # Mapeando y exportando a GIS

    pointgdf = gpd.GeoDataFrame(dffinal, geometry=[Point(x, y) for x, y in zip(dffinal.lng, dffinal.lat)])

    pointgdf['ok'] = pointgdf['ok'].astype('int')

    pointgdf2=pointgdf[['Unnamed: 0', 'Barrio', 'Direccion', 'Provincia', 'address','confidence', 'lat', 'lng', 'ok', 'raw.extent.ymin', 'raw.feature.attributes.Addr_Type',
           'raw.feature.attributes.Score', 'raw.feature.geometry.x',
           'raw.feature.geometry.y', 'raw.name', 'score', 'status', 'geometry']]

    pointgdf2.to_file("resultados_geo.shp")

if __name__ == "__main__":

    #queryinscriptions()
    print('georef correctamente importado')