#!venv/bin/python
"""Paquete encargado de la gestión y representación de un dispositivo servo, para reducir la carga a la clase
principal """
from time import sleep

from gpiozero import AngularServo

import config

MIN_PULSE_WIDTH = 35 / 100000  # 0.35ms
MAX_PULSE_WIDTH = 200 / 100000  # 2ms
SPEED = 20 / 1000  # 20ms corresponde con la frecuencia del SG90
SLEEP_TIME = 0.2


class Cerradura(AngularServo):
    """
    Clase que representa el elemento que actuará como cerradura en el sistema
    Cambiamos la especificación por defecto, para poder controlar los 180º que nos permite el modelo de servo SG90
    @see https://gpiozero.readthedocs.io/en/stable/api_output.html#angularservo
    """

    MID_ANGLE: float = 90
    MIN_ANGLE: float = 0
    MAX_ANGLE: float = 180

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

    def __init__(self, pin=None, pin_factory=None):
        self.logger = config.log.getLogger(__name__)
        self.logger.info("Creando la cerradura")
        self._estado = None
        super(Cerradura, self).__init__(pin, self.MID_ANGLE, self.MIN_ANGLE, self.MAX_ANGLE, MIN_PULSE_WIDTH,
                                        MAX_PULSE_WIDTH, SPEED,
                                        pin_factory=pin_factory)
        sleep(1)
        self.abrir()
        sleep(1)
        self.cerrar()
        sleep(1)
        self.abrir()
        self.logger.info("Cerradura correcta\n")

    def abrir(self):
        """
        Este método gira el elemento que represente la cerradura hasta una posición que permita mantener la puerta
        desbloqueda
        """
        self.max()
        sleep(SLEEP_TIME)
        self.estado = self.angle
        self.angle = None

    def cerrar(self):
        """
        Este método gira el elemento que represente la cerradura hasta una posición que permita mantener la puerta bloqueda
        """
        self.mid()
        sleep(SLEEP_TIME)
        self.estado = self.angle
        self.angle = None

    def __del__(self):
        self.logger.debug("Eliminando el servo")
        try:
            if self:
                self.abrir()
                sleep(SLEEP_TIME)
                self.close()
        except Exception as e:
            self.logger.error("No se ha podido eliminar el servo como se esperaba:\n\t" + str(e))

    @property
    def estado(self) -> str:
        """
        @return: el estado de la cerradura
        """
        return self._estado

    @estado.setter
    def estado(self, value):
        if value == self.MID_ANGLE:
            self._estado = "CERRADO"
        if value == self.MAX_ANGLE:
            self._estado = "ABIERTO"
