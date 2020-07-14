from lsst.ts import salobj
from lsst.ts.adamSensors.model import AdamModel
import pathlib
import asyncio


class AdamCSC(salobj.ConfigurableCsc):
    """
    CSC for simple sensors connected to an ADAM controller
    """

    def __init__(self, config_dir=None, initial_state=salobj.State.STANDBY, initial_simulation_mode=0):
        schema_path = pathlib.Path(__file__).resolve().parents[4].joinpath("schema", "AdamSensors.yaml")
        super().__init__("AdamSensors", index=0, schema_path=schema_path, config_dir=config_dir,
                         initial_state=initial_state, initial_simulation_mode=initial_simulation_mode)

        self.connected = False
        self.adam = None
        self.config = None

        # setup asyncio tasks for the loop
        done_task = asyncio.Future()
        done_task.set_result(None)
        self.telemetryLoopTask = done_task

    async def begin_start(self, id_data):
        await super().begin_start(id_data)
        self.adam = AdamModel(self.log, simulation_mode=True)
        await self.adam.connect(self.config.ip, self.config.port)

    async def telemetry_loop(self):
        """
        The main process of this CSC, periodically reads the voltages off
        the ADAM device, converts them into the appropriate units
        for various sensor types, and publishes them as telemetry
        """

        while self.connected:
            voltages = self.adam.read_voltage()


    @staticmethod
    def get_config_pkg():
        return("ts_config_???")

    async def configure(self, config):
        print('csc config')
        self.config = config
