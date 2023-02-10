#!venv/bin/python
"""Código para la gestionar el acceso a un recinto.
El sistema leera una tarjeta RFID, la cotejará con el sistema central, mandando la id de la tarjeta mediante Zigbee
Si la respuesta es afirmativa, abrirá la cerradura de la puerta representada con un serbo, y pintará el LED verde, en
caso contrário, pintará el led rojo"""

# Gestionamos el tipo de ejecución que se va a realizar
import argparse
# Cargamos la configuración
import logging
import sys

import config
from watchDog.watchDog import WatchDog


def get_parser():
    """
    Creates a new argument parser.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-R', '--remote', dest="remote",
                        help="Defino que tipo de ejecución se va a realizar, remota o local, True o False, "
                             "respectivamente",
                        default=config.remote)
    return parser


logger = logging.getLogger(__name__)
logger.setLevel(config.log_level)
logger.addHandler(config.warn_file_handler)
logger.addHandler(config.log.StreamHandler())


def main(args=None):
    """
    Main entry point for your project.
    Args:
        args : list
            A of arguments as if they were input in the command line. Leave it
            None to use sys.argv.
    """

    assert (config.env is not None), "No se ha podido recuperar la información de configuración"

    parser = get_parser()
    args = parser.parse_args(args)
    stapleton = WatchDog(remote=config.remote, logger=logger)
    stapleton.wake_up()


if __name__ == "__main__":
    try:
        logger.info("Starting the program")
        main()
        logger.info("Ejecución finalizada")
        sys.exit(0)
    except KeyboardInterrupt:
        logger.warning("Proceso abortado por el usuario")
        sys.exit(0)
    except Exception as e:
        logger.error("Algo no fue como se esperaba:\n{}".format(e))
        sys.exit(1)
