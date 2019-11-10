# Descripcion

El programa georef permite geocodifcar de manera automatizada una lista de direcciones guardadas en un archivo.csv
El archivo csv tiene que tener una primera fila indicando "Direccion" al nombre de la columna donde van las direcciones.
La función guarda un archivo excel el detalle de los resultados y también un shapefile con los datos georeferenciados.

# Requerimientos

Python 3.7, Pandas, Geopandas, Geocoder

# Instalación

La instalacion de todas las librerias necesarias es llevada a cabo por Miniconda. Instalar primero [Miniconda](https://docs.conda.io/en/latest/miniconda.html#windows-installers).
De no tener [Python](https://www.python.org/downloads/release/python-374/) instalarlo también.

Copiar los archivos de este repositorio a un directorio y desde ahí, usando la linea de comando (CMD), correr el siguiente comando para la instalacion de lo necesario.

```
conda env create -f environment.yml
```

Activar el ambiente virtual

```
conda activate geoprogram
```

# Como usar el programa

Desde la linea de comando de python, importar georef.
Luego utilizar la siguiente sintaxis para definir el nombre del archivo csv. Usar comillas para especificar el nombre del archivo:

```
> python

> import georef

> georef.georef('santiago_direcciones_prueba.csv')
```

