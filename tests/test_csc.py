import unittest

import asynctest

from lsst.ts import salobj
from lsst.ts import adamSensors


STD_TIMEOUT = 15  # standard command timeout (sec)


class CscTestCase(salobj.BaseCscTestCase, asynctest.TestCase):
    def basic_make_csc(self, initial_state, config_dir, simulation_mode):
        return adamSensors.adamSensorsCSC.AdamCSC(initial_state=initial_state, config_dir=config_dir)

    async def test_one(self):
        async with self.make_csc(
            initial_state=salobj.State.STANDBY,
            config_dir="/home/saluser/gitdir/ts_config_eas/AdamSensors/v1/",  # make this smarter some day
            simulation_mode=1,
        ):
            await self.remote.cmd_start.set_start(settingsToApply="homeoffice_pandemic_test.yaml")


if __name__ == "__main__":
    unittest.main()
