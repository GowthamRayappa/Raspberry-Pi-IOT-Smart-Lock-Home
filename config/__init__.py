#!venv/bin/python
"""Paquete que controla los ficheros de configuración del proyecto"""

import logging
# Cargamos los datos del fichero de configuración
import os
from configparser import ConfigParser
from os import scandir, getcwd
from os.path import abspath
from typing import List, Union

from watchDog import xbee

sufixMySQL = '.mysql'

loaded = False

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
try:
    warn_file_handler = logging.FileHandler("log/log.log")
except FileNotFoundError:
    os.mkdir("log")
    warn_file_handler = logging.FileHandler("log/log.log")
warn_file_handler.setLevel(logging.WARN)
logger.addHandler(warn_file_handler)
logger.addHandler(logging.StreamHandler())


def read_config(cfg_files) -> ConfigParser:
    """
    Lee los parámetros fijados en los ficheros de configuración
    :param cfg_files:
    :return: los parámetros del fichero de configuración
    @param cfg_files:
    @return:
    @rtype: ConfigParser
    """

    assert (cfg_files is not None), "Ups, no se ha podido encontrar nigún fichero de configuración."

    logger.info("Leyendo configuración ...")
    logger.info("Ficheros a tratar:\t" + str(cfg_files))

    if cfg_files is not None:
        logger.debug("Se han recibido los ficheros")
        config_properties = ConfigParser()
        if config_properties is None:
            raise ValueError("No se han escontrado parametros de configuración", cfg_files)
        else:
            logger.info("Configurador de propiedades cargado")

        # merges all files into a single config
        for i, cfg_file in enumerate(cfg_files):
            logger.info("Preparandose para tratar el fichero:\t" + cfg_file)
            if os.path.exists(cfg_file):
                config_properties.read(cfg_file)
                logger.info("\tExtrayendo configuración del fichero:\t" + cfg_file)
            else:
                raise FileNotFoundError("No se ha posido encontrar el fichero", cfg_file, str(os.listdir))

        return config_properties
    else:
        raise ValueError("No se han podido tratar los ficheros.", cfg_files)


def ls_file(ruta=getcwd()) -> List[Union[bytes, str]]:
    """

    :param ruta:
    :return:
    @rtype: List[Union[bytes, str]]
    @param ruta:
    @return:
    """
    return [arch.name for arch in scandir(ruta)]


def ls_a(ruta=getcwd()) -> List[Union[bytes, str]]:
    """
        :param ruta:
        :return:
        @rtype: List[Union[bytes, str]]
        @param ruta:
        @return:
    """
    return [abspath(arch.path) for arch in scandir(ruta)]


def search_xbee_port() -> str:
    """
        Busca entre los dispositivos usb insertado, si contiene alguna de las palabras clave
        relacionadas.
        @see watchDog/xbee.py:7
    """
    route = None

    """
        Si el parámetro está indicado, lo copiamos.
        Esto será si previamente sabemos que la antena está en ese lugar montada"""
    route = parameters.get('xbee', 'route')
    if not route:
        # serial.tools.list_ports.comports()
        route = xbee.encontrar_rutas()
        if not route:
            raise Exception("No se ha podido encontrar ninguna ruta donde esté montada ninguna antena XBee")

    """En otro caso, ejecutamos un script, que la descubra
    Partiendo de la suposición de que la antena no está previamente montada
    detectará el nuevo dispositivo y se lo asignará como punto de montaje de la antena
    """

    return route


# merge all into one config dictionary
parameters = read_config(['env.ini', 'local.ini'])

__project = None
__version = None
__description = None
__autor = None

# Formato de los mensajes de logging
log_format = None
log_level = None
log_file = None
warn_log_file = None
log = None

"""Definición de las variables de configuración"""
# Dirección del host remoto
remote_host = None

# LED's
pin_error = None
pin_warn = None
pin_monitor = None
pin_success = None
# Servo
pin_servo = None
# XBee
xbee_port = None
xbee_baudrate = None
xbee_route = None
mac_puerta = None
mac_router = None

# Variable para definir si la ejecución es en remoto o en local
remote = False

# Recuperamos la información del fichero de configuración
if parameters.__len__() > 1:
    # get the current branch (from local.ini)
    env = parameters.get('branch', 'env')
    remote = parameters.get('branch', 'remote')
    remote_host = parameters.get('remote', 'host')  # Configurado en local.ini

    # Formato a aplicar en los print del log
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    # log_format = parameters.get(env + '.log', 'format')
    log_level = logging.getLevelName(parameters.get(env + '.log', 'level'))
    log_file = parameters.get(env + '.log', 'file_log')
    warn_log_file = parameters.get(env + '.log', 'warn_log_file')

    log = logging
    log.basicConfig(level=log_level,
                    format=log_format,
                    filename=log_file)
    warn_file_handler = log.FileHandler(warn_log_file)
    warn_file_handler.setLevel(logging.WARN)
    formatter = logging.Formatter(log_format)
    warn_file_handler.setFormatter(formatter)

    # proceed to point everything at the 'branched' resources
    dbUrl = parameters.get(env + sufixMySQL, 'dbUrl')
    dbUser = parameters.get(env + sufixMySQL, 'dbUser')
    dbPwd = parameters.get(env + sufixMySQL, 'dbPwd')
    dbName = parameters.get(env + sufixMySQL, 'dbName')

    # global values
    __project = parameters.get('global', '__project__')
    __version = parameters.get('global', '__version__')
    __description = parameters.get('global', '__description__')
    __autor = parameters.get('global', '__autor__')

    # Carga de los pines
    pin_error = parameters.get('pin', 'error')
    pin_warn = parameters.get('pin', 'warn')
    pin_monitor = parameters.get('pin', 'monitor')
    pin_success = parameters.get('pin', 'success')
    pin_servo = parameters.get('pin', 'servo')

    # Info del xbee
    xbee_baudrate = parameters.get('xbee', 'baudrate')
    # Lugar donde estará montado la antena
    xbee_port = search_xbee_port()
    # Dirección mac del dispositivo que estará situado en la puerta
    mac_puerta = parameters.get('xbee.mac', 'puerta')
    # Dirección mac del dispositivo que gestionará los periféricos
    mac_router = parameters.get('xbee.mac', 'router')

    # Listado de acciones configuradas
    action_in = parameters.get('action', 'in').split()
    action_out = parameters.get('action', 'out').split()

    logger.info("Configuración recuperada correctamente.")

    loaded = True
