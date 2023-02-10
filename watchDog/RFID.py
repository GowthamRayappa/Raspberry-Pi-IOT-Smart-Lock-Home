#!venv/bin/python
"""
    Paquete encargado de la gestión y representación de un dispositivo lector de tarjetas RFID.
    Como el sistema sobre el que se está desarrollando es una Raspberry Pi Zero, tras activar el controlador del puerto SPI,
    tenemos que los dos puertos disponibles son: /dev/spidev0.0 (para el ejemplo usaremos el 0 - pin(24) - GPIO8 - SPICS0 ) y /dev/spidev0.1

"""
from mfrc522 import SimpleMFRC522

import config


class RFID(object):
    """
    Clase que representa el dispositivo lector de tarjetas RFID
    """

    CHANNEL: int = 0
    CHIP_SELECT: int = 0

    @property
    def logger(self):
        """

        @return:
        """
        return self._logger

    @logger.setter
    def logger(self, value):
        self._logger = value
        self.logger.setLevel(config.log_level)
        self.logger.addHandler(config.warn_file_handler)
        self.logger.addHandler(config.log.StreamHandler())

    @property
    def device(self):
        """
        Dispositivo que encaspulará el objeto de la librería externa que se represente
        @return:
        """
        return self._device

    @device.setter
    def device(self, value):
        self._device = value

    def __init__(self):
        self.device = SimpleMFRC522()
        self.logger = config.log.getLogger(__name__)
        self.logger.info("Lector de tarjetas montado")

    def leer_tarjeta(self) -> str:
        """
            Lee la tarjeta sin bloquear el proceso y retona la id de la misma
        """
        try:
            # id, text = self.device.read()
            id_tag = self.device.read_id_no_block()
            return id_tag
        except Exception as ki:
            self.logger.error(str(ki))
            raise

    def esperar_hasta_leer_tarjeta(self) -> str:
        """
            Lee la tarjeta sin bloquear el proceso y retona la id de la misma
        """
        self.logger.info("Esperando para leer tarjeta")
        try:
            id_tag = self.device.read_id()
            self.logger.info("Tarjeta leida {}".format(id_tag))
            return id_tag
        except Exception as ki:
            self.logger.error(str(ki))
            raise
