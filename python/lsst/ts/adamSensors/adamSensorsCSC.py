from lsst.ts import salobj
from lsst.ts.adamSensors.model import AdamModel
from numpy import poly1d
import pathlib
import asyncio
import concurrent


class AdamCSC(salobj.ConfigurableCsc):
    """
    CSC for simple sensors connected to an ADAM controller
    """

    def __init__(self, config_dir=None, initial_state=salobj.State.STANDBY, initial_simulation_mode=0):
        schema_path = pathlib.Path(__file__).resolve().parents[4].joinpath("schema", "AdamSensors.yaml")
        super().__init__(
            "AdamSensors",
            index=0,
            schema_path=schema_path,
            config_dir=config_dir,
            initial_state=initial_state,
            initial_simulation_mode=initial_simulation_mode,
        )

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
        loop = asyncio.get_event_loop()
        executor = concurrent.futures.ThreadPoolExecutor()
        await loop.run_in_executor(executor, self.adam.connect, self.config.adam_ip, self.config.adam_port)
        self.connected = True
        await self.telemetry_loop()

    async def telemetry_loop(self):
        """
        The main process of this CSC, periodically reads the voltages off
        the ADAM device, converts them into the appropriate units
        for various sensor types, and publishes them as telemetry
        """
        # set up dictionary
        sensors = {
            0: (self.config.analog_input_0_type, poly1d(self.config.analog_input_0_coefficients)),
            1: (self.config.analog_input_1_type, poly1d(self.config.analog_input_0_coefficients)),
            2: (self.config.analog_input_2_type, poly1d(self.config.analog_input_0_coefficients)),
            3: (self.config.analog_input_3_type, poly1d(self.config.analog_input_0_coefficients)),
            4: (self.config.analog_input_4_type, poly1d(self.config.analog_input_0_coefficients)),
            5: (self.config.analog_input_5_type, poly1d(self.config.analog_input_0_coefficients)),
        }

        # figure out which topics to publish
        hasTemperature = False
        hasPressure = False
        for s in sensors:
            if sensors[s][0] == "Pressure":
                hasPressure = True
            if sensors[s][0] == "Temperature":
                hasTemperature = True

        loop = asyncio.get_event_loop()
        executor = concurrent.futures.ThreadPoolExecutor()

        outputs = [0, 0, 0, 0, 0, 0]
        while self.connected:
            voltages = await loop.run_in_executor(executor, self.adam.read_voltage)

            # convert the voltage into whatever units, according to the
            # polynomial defined in configuration
            for i in range(6):
                outputs[i] = sensors[i][1](voltages[i])

            # Assemble telemetry topics
            # Channel 0
            if sensors[0][0] == "Pressure":
                self.tel_pressure.set(pressure_ch0=outputs[0])
            elif sensors[0][0] == "Temperature":
                self.tel_temperature.set(temp_ch0=outputs[0])

            # Channel 1
            if sensors[1][0] == "Pressure":
                self.tel_pressure.set(pressure_ch1=outputs[1])
            elif sensors[1][0] == "Temperature":
                self.tel_temperature.set(temp_ch1=outputs[1])

            # Channel 2
            if sensors[2][0] == "Pressure":
                self.tel_pressure.set(pressure_ch2=outputs[2])
            elif sensors[2][0] == "Temperature":
                self.tel_temperature.set(temp_ch2=outputs[2])

            # Channel 3
            if sensors[3][0] == "Pressure":
                self.tel_pressure.set(pressure_ch3=outputs[3])
            elif sensors[3][0] == "Temperature":
                self.tel_temperature.set(temp_ch3=outputs[3])

            # Channel 4
            if sensors[4][0] == "Pressure":
                self.tel_pressure.set(pressure_ch4=outputs[4])
            elif sensors[4][0] == "Temperature":
                self.tel_temperature.set(temp_ch4=outputs[4])

            # Channel 5
            if sensors[5][0] == "Pressure":
                self.tel_pressure.set(pressure_ch5=outputs[5])
            elif sensors[5][0] == "Temperature":
                self.tel_temperature.set(temp_ch5=outputs[5])

            # publish telemetry
            if hasPressure:
                self.tel_pressure.put()
            if hasTemperature:
                self.tel_temperature.put()

            asyncio.sleep(1)

    @staticmethod
    def get_config_pkg():
        return "ts_config_eas"

    async def configure(self, config):
        print("csc config")
        self.config = config
