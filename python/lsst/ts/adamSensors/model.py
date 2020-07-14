from pymodbus.client.sync import ModbusTcpClient as ModbusClient
from pymodbus.exceptions import ConnectionException, ModbusIOException


class AdamModel():
    """
    Class that reads sensor voltage(s) through an ADAM 6024 device

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

    def __init__(self, log, simulation_mode=False):
        self.client = None
        self.clientip = None
        self.clientport = None
        self.log = log

        self.range_size = 20
        self.range_start = -10 # zero point offset for the ADAM device
        self.simulation_mode = simulation_mode

    def connect(self, ip, port):
        self.clientip = ip
        self.clientport = port
        if simulation_mode:
            self.client = None
        else:
            self.client = ModbusClient(self.clientip, self.clientport)

    def disconnect(self):
        self.client.close()

    def read_voltage(self):
        """ reads the voltage off of ADAM-6024's inputs for channels 0-5.

        Parameters
        ----------
        None

        Returns
        -------
        volts : List of floats
            the voltages on the ADAM's input channels
        """
        if simulation_mode:
            return [0,0,0,0,0,1.25]
            
        else:
            try:
                readout = self.client.read_input_registers(0, 8, unit=1)
                return [self.counts_to_volts(r) for r in readout.registers]
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

    def counts_to_volts(self, counts):
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
        ctv = self.range_size/65535
        return counts * ctv + self.range_start
