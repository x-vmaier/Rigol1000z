import pyvisa as visa
import Rigol1000z
from time import sleep

rm = visa.ResourceManager()

# We are connecting the oscilloscope through USB here.
# Only one VISA-compatible instrument is connected to our computer,
# thus the first resource on the list is our oscilloscope.
# You can see all connected and available local devices calling
#

osc_resource: visa.Resource = rm.open_resource(rm.list_resources()[0])

with Rigol1000z.Rigol1000z(osc_resource) as osc:
    print(type(osc[1]))

    # Change voltage range of channel 1 to 50mV/div.
    osc[1].set_vertical_scale_v(50e-3)

    osc.run()
    sleep(0.5)

    # Stop the scope.
    osc.stop()

    # Take a screenshot.
    # osc.get_screenshot('screenshot.png', 'png')

    # Capture the data sets from channels 1--4 and
    # write the data sets to their own file.
    # for c in range(1, 4):

    # osc[c].get_data('raw', 'channel%i.dat' % c)
    osc[1].get_data('raw', './channel1.csv')

print("done")
