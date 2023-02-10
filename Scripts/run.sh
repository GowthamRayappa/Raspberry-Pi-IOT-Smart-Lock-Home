#!/bin/bash
#Script que ejecuta el código de la puerta en local
cd ~/Dev/Zero-Project || { echo "No se ha encontrado la ruta"; exit 1;}
python3 __main__.py -R False