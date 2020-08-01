import pyvisa as visa
import Rigol1000z
from Rigol1000z.constants import EWaveformMode

# Initialize the visa resource manager
rm = visa.ResourceManager()

# Get the first visa device connected
osc_resource = rm.open_resource(rm.list_resources()[0])

# Create oscilloscope interface
with Rigol1000z.Rigol1000z(osc_resource) as osc:

    # start with known state by restoring default settings
    osc.ieee488.reset()

    # run data acquisition
    osc.run()

    # Change voltage range of channel 1 to 50mV/div.
    osc[1].scale_v = 50e-3

    # Autoscale the scope
    osc.autoscale()

    # Stop the scope in order to collect data.
    osc.stop()

    # Take a screenshot of the scope's display
    osc.get_screenshot('screenshot.png', 'png')

    # todo: collect data from all enabled channels of the scope
    osc.get_data(EWaveformMode.Raw, './channel1.csv')

    # Move back to run mode when data collection is complete
    osc.run()

print("done")
