__author__ = 'Ricardo Pasquini'

from shapely import wkt
import geopandas as gpd
import pandas as pd
import os
import inspect
import pickle
import geocoder
from shapely.geometry import Point
from itertools import islice
import pymongo
import matplotlib.pyplot as plt

client = pymongo.MongoClient('localhost', 27017)
db = client["vivienda"]  #vivienda is the name of the db

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
print(currentdir)
#datos de la proyeccion en la que voy a trabajar
crs={'proj': 'tmerc', 'lat_0': -34.6297166, 'lon_0': -58.4627, 'k': 0.999998, 'x_0': 100000, 'y_0': 100000, 'ellps': 'intl', 'units': 'm', 'no_defs': True}


def load_direcciones_con_barrios():
    filename = "Direcciones.xlsx"
    df=pd.read_excel(currentdir+'\\datos_vivienda_social\\barrios_santiago\\'+filename)
    #df=df.rename(index=str, columns={" DOMICILIO  ": "DIRECCION", " NDOC  ": 'DNI_TITULAR'})
    df.index=df['index'].astype(str)
    return df


def load_direcciones_originales():
    "Levanta las direcciones orginales guardadas en un pickled dataframe"
    pickle_in=open(currentdir+'\\dataframes\\demanda_santiago_original.pickle', 'rb')
    df = pickle.load(pickle_in)
    return df

def prepara_gdf_con_barrio():
    "procedimiento completo para armar el gdf con barrios"

    df=load_direcciones_con_barrios()
    df0=load_direcciones_originales()
    df=df[['DIRECCION', 'Barrio normalizado', 'Ciudad', 'BASE', 'ID BASE',
           'LAT_CENTROIDE', 'LONG_CENTROIDE', 'WKT_POLYGON']].join(df0[['DIRECCIONsinBarrio', 'DNI_TITULAR']])
    # agrego la variable proximity, combinacion de lat y long que la necesito para la georef
    df['proximity']="["+df['LAT_CENTROIDE'].astype('str')+","+df['LONG_CENTROIDE'].astype('str')+"]"

    # Me quedo solo con las observaciones que tienen  barrios
    df_con_barrio=df[df['WKT_POLYGON'].isnull()==False]
    # Preparo los poligonos en wkt to coordenadas
    df_con_barrio['Coordinates']=df_con_barrio['WKT_POLYGON'].apply(wkt.loads)
    gdf_con_barrio = gpd.GeoDataFrame(df_con_barrio, geometry='Coordinates',crs={'init':'epsg:4326'})
    #reproyectando
    gdf_con_barrio=gdf_con_barrio.to_crs(crs)
    return gdf_con_barrio

def check_results(index, geocoderesults, gdf_con_barrio, graph=False):

    """A partir de un geocoderesult va a chequear si está en el barrio respectivo,  y si esta afuera calcular la distancia

    Como va a ser usado como parte de un loop, necesita el index para saber en que observacion del df pertenece el geocoderesult

    """
    lat=geocoderesults.json['lat']
    lng=geocoderesults.json['lng']
    #geometry = [Point(xy) for xy in zip(cities['longitude'], cities['latitude'])]
    point=Point(lng,lat)
    fake=pd.DataFrame(
        {'hola':[1], 'lat':lat, 'lng':lng})
    geometry = [Point(xy) for xy in zip(fake['lng'], fake['lat'])]
    pointgpd=gpd.GeoDataFrame(fake,geometry=geometry,crs={'init':'epsg:4326'})
    #reprojecting
    pointgpd=pointgpd.to_crs(crs)

    #obtengo el barrio como poligono
    geom=gdf_con_barrio[gdf_con_barrio.index==index]
    pointisinside=pointgpd.geometry[0].within(geom.geometry.values[0])
    result={'pointisinside':pointisinside}

    if pointisinside:
        distance=0
        result.update( {'distance' : distance} )
    else:
        distance=pointgpd.geometry[0].distance(geom.geometry.values[0])
        result.update( {'distance' : distance} )

    if graph==True:
        fig, myax = plt.subplots()
        pointgpd.plot(ax=myax)
        gdf_con_barrio[gdf_con_barrio.index==index].plot(ax=myax)


    return result



def iterador(gdf_con_barrio, saveindb=False, **kwargs):
    #LIMIT = 4
    LIMIT=kwargs.get('LIMIT', False)
    graph=kwargs.get('graph', False)

    # iterrows and unpacking
    if LIMIT is False:
        iteraciones=gdf_con_barrio.iterrows()
    else:
        iteraciones=islice(gdf_con_barrio.iterrows(), LIMIT)

    for index, row in iteraciones:
            print(index)
            addressstring=row['DIRECCIONsinBarrio']+', Santiago del Estero, Argentina'
            #addressstring=row['DIRECCIONsinBarrio']+', Santiago del Estero, Argentina'
            #print(addressstring)
            geocoderesults=geocoder.arcgis(addressstring, proximity=row['proximity'])
            #print({'id':index,'geocoderesults':geocoderesults.json})

            #check_results is the function that computes distance
            result=check_results(index, geocoderesults, gdf_con_barrio, graph==graph)
            #print(result)

            address=geocoderesults.json['address']
            lat=geocoderesults.json['lat']
            lng=geocoderesults.json['lng']
            ok=geocoderesults.json['ok']
            quality=geocoderesults.json['quality']
            score=geocoderesults.json['score']

            if saveindb:
                db.santiagov3.insert({'id':index,'DNI_TITULAR':row['DNI_TITULAR'],
                                      'address':address,
                                      'lat':lat,
                                      'lng':lng,
                                      'ok':ok,
                                      'quality':quality,
                                      'score':score,
                                      'pointisinside':result['pointisinside'], 'distance':result['distance']})