from pymodbus.client.sync import ModbusTcpClient as ModbusClient
from pymodbus.exceptions import ConnectionException, ModbusIOException


class TransducerModel():
    """
    Class that reads the transducer voltage through an ADAM 6024 device

        Parameters
        ----------
        ip : string
            the IP address of the ADAM 6024 controller
        port : int
            the port number for the ADAM 6024 controller

        Attributes
        ----------
        client : ModbusClient
            the pymodbus object representing the ADAM 6024
    """

    def __init__(self, ip, port):
        self.client = None
        self.clientip = ip
        self.clientport = port

    def connect(self):
        self.client = ModbusClient(self.clientip, self.clientport)

    def _readVoltage(self):
        """ reads the voltage off of ADAM-6024's inputs for channels 0-3.

        Parameters
        ----------
        None

        Returns
        -------
        volts : List of floats
            the voltages on the ADAM's first 4 input channels
        """
        try:
            readout = self.client.read_input_registers(0, 8, unit=1)
            return [self._countsToVolts(r) for r in readout.registers]
        except AttributeError:
            # read_input_registers() *returns* (not raises) a
            # ModbusIOException in the event of loss of ADAM network
            # connectivity, which causes an AttributeError when we try
            # to access the registers field. But the whole thing is
            # really a connectivity problem, so we re-raise it as a
            # ConnectionException, which we know how to handle. Weird 
            # exception handling is a known issue with pymodbus so it
            # may see a fix in a future version, which may require 
            # minor code changes on our part.
            # https://github.com/riptideio/pymodbus/issues/298
            raise ConnectionException

    def _countsToVolts(self, counts):
        """ converts discrete ADAM-6024 input readings into volts

        Parameters
        ----------
        counts : integer
            16-bit integer received from ADAM device

        Returns
        -------
        volts : float
            counts converted into voltage number
        """
        ctv = 20/65535
        return counts * ctv - 10