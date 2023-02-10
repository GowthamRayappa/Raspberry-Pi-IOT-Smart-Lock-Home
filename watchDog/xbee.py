#!venv/bin/python
"""Paquete encargado de la gestión y representación de un dispositivo ZigBee/Xbee"""

import serial.tools.list_ports
from digi.xbee.devices import ZigBeeDevice, RemoteZigBeeDevice
from digi.xbee.exception import XBeeException
from digi.xbee.models.address import XBee64BitAddress, XBee16BitAddress
from digi.xbee.models.message import XBeeMessage
from digi.xbee.models.status import TransmitStatus
from digi.xbee.packets.common import TransmitStatusPacket

import config

"""Lista de palabras que podría contener un shield con una antena xbee"""
xbeeAntenaWhiteList = ['FT232R', 'UART']
PING = "CMD:PING"


def encontrar_rutas() -> []:
    """Método que retorna una lista de posibles rutas donde se encontrará un dispositivo compatible con una antena
     XBEE conectada mediante un shield USB"""

    ports = serial.tools.list_ports.comports()
    filtered = []
    for port, desc, hwid in sorted(ports):
        for word in desc.split(' '):
            if word in xbeeAntenaWhiteList:
                filtered.append(port)
                break
    return filtered


class XBee(ZigBeeDevice):
    """Clase que representa las antenas xbee que serán la principàl interface de comunicación del dispositivo
    WatchDog
    @see https://xbplib.readthedocs.io/en/stable/index.html"""

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

    def __init__(self, port_list, baud_rate, remote_mac=None):
        """Instanciamos una antena XBeee a partir de un dispositivo ZigBeeDevice
        @param port_list Lista de puertos en los que se podría encontrar la antena conectada
        @param baud_rate Frecuencia de trabajo de la antena
        @param remote_mac [Opcional] Dirección mac a de la antena a la que se conectará"""

        self.logger = config.log.getLogger(__name__)
        self.logger.info("Creando la antena")
        """De la lista de posibles puertos a la que pueda estár conectada la antena
        nos conectamos a la primera y lo notificamos"""
        self.logger.info("Puertos encontrados: " + str(port_list))
        self.logger.info("Frecuencia de trabajo: " + str(baud_rate))
        self.logger.info("Enlace remoto: " + str(remote_mac))
        for port in port_list:
            self.logger.info("Probando el puerto: " + port)
            try:
                super().__init__(port, baud_rate)
            except Exception as e:
                self.logger.error("Encontrado un error al inicializar el dispositivo ZigBeeDevice\n" + str(e))
                raise e

            try:
                super().open()
                if remote_mac is not None:
                    self.remote_Zigbee = remote_mac

                # Nos disponemos a escuchar el medio
                # super().add_data_received_callback(self.__tratar_entrada)
            except XBeeException as e:
                self.logger.error("No se ha podido conectar con la antena XBee.\n\t" + str(e))
                super().close()
            else:
                antena = str(super().get_node_id() + "(" + str(super().get_64bit_addr()) + ")")
                self.logger.info("\tConectada la antena '" + antena + "' al puerto " + port + "\n")
                break

    def __del__(self):
        self.logger.debug("Eliminando el ZigBee")
        try:
            if self:
                super().del_data_received_callback(self.__tratar_entrada)
        except Exception as e:
            self.logger.error("No se ha cerrado la conexíón de la antena\n\t" + str(e))

    def __str__(self):
        atr: dict = {'Opened': self.is_open(), 'Name': self.get_node_id(), 'Dir': str(self.get_64bit_addr()),
                     'Remote_dir': str(self.remote_Zigbee.get_64bit_addr())}

        return format(atr)

    @property
    def remote_Zigbee(self) -> RemoteZigBeeDevice:
        """
        @return Retorna el dispositivo remoto al que se encuentra conectado la antena
        @rtype: RemoteZigBeeDevice
        """
        return self.__remote

    @remote_Zigbee.setter
    def remote_Zigbee(self, mac):
        self.__remote = RemoteZigBeeDevice(self, XBee64BitAddress.from_hex_string(mac))

    def mandar_mensage(self, msg=PING) -> bool:
        """
            Manda el mensaje al destinatario por defecto.
        """
        ack: TransmitStatusPacket = None
        # Transformamos el mensaje recibido en un string tratable
        msg = str(msg)
        # Recuperamos la dirección del dispositivo remoto en formato de 64 bits
        high = self.remote_Zigbee.get_64bit_addr()
        # Recuperamos la dirección del dispositivo remoto en 16 bits o la marcamos como desconocida
        low = self.remote_Zigbee.get_16bit_addr() or XBee16BitAddress.UNKNOWN_ADDRESS
        try:
            # Intentamos mandar el mensaje
            ## Versión sin fragmentar el paquete
            ack = super().send_data_64_16(high, low, msg)
            self.logger.debug(format(ack))
            if ack.transmit_status is not TransmitStatus.SUCCESS:
                self.logger.warning(format(ack))

        except Exception as e:
            self.logger.error("Se ha encontrado un error al mandar el mensaje\n\t" + str(e))
            # Añadir código para el reintento
        else:
            # TODO Borrar esta traza de control
            self.logger.info("Mandado mensaje:\t" + msg)
            return ack.transmit_status is TransmitStatus.SUCCESS

    def __tratar_entrada(self, recived_msg: XBeeMessage):
        """
            Tratamos la información que recibamos
        @param recived_msg:
        """
        msg = recived_msg.data.decode("utf8")
        self.logger.debug(msg)
        super().close()

    def escuchar_medio(self) -> str:
        """
        Escucha por si enlace le manda algún mensaje
        @return: El mensaje recibido si hay algo, None eoc
        """
        recived_msg = None
        if self.is_open:
            recived_order = self.read_data()
            if recived_order is not None:
                recived_msg = str(recived_order.data.decode("utf8"))

        return recived_msg

    def esperar_hasta_recibir_orden(self) -> str:
        """
            Bucle que no finaliza hasta que se recibe un mensaje
            @return El mensaje recibido, None si la antena está cerrada
        """
        recived_msg = None
        if self.is_open():
            recived_order = None
            while recived_order is None:
                recived_order = self.read_data()
                if recived_order is not None:
                    recived_msg = str(recived_order.data.decode("utf8"))

        return recived_msg
