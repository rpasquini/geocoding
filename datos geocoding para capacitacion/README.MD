# Descripcion

La funcion georef permite geocodifcar de manera automatizada una lista de direcciones guardadas en un archivo.csv
La función guarda un archivo excel con el detalle de los resultados y también un shapefile.

# Instalacion
Se recomienda instalar primero [Miniconda](https://docs.conda.io/en/latest/miniconda.html#windows-installers)

Copiar los archivos de este repositorio a un directorio y desde ahí correr el siguiente comando para la instalacion de lo necesario.

conda env create -f environment.yml

Activar el ambiente virtual

conda activate geoprogram

# Como usar el programa

Desde la linea de comando de python, importar georef.
Luego utilizar la siguiente sintaxis para definir el nombre del archivo csv:

```
> python

> import georef

> georef.georef('santiago_direcciones_prueba.csv')
```

