# Rigol1000z
Python library to control Rigol DS1000z series oscilloscopes based on the VISA protocol (PyVISA). The oscilloscope can be connected either by USB or by Ethernet to the local network (See PyVISA docs for more information).

Tested on Windows 10.

## Dependencies
* [python3.7](https://www.python.org/downloads/release)
* [numpy](https://github.com/numpy/numpy)
* [pyvisa](https://github.com/pyvisa/pyvisa)
* [tqdm](https://github.com/tqdm/tqdm)

## Recommended
* [pipenv](https://pypi.org/project/pipenv/) makes 

## Example
```python
import pyvisa as visa
import Rigol1000z
from Rigol1000z.constants import EWaveformMode

# Initialize the visa resource manager
rm = visa.ResourceManager()

# Get the first visa device connected
osc_resource = rm.open_resource(rm.list_resources()[0])

# Create
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
```

## Acknowledgements
Based on the original work by [@jtambasco](https://github.com/jtambasco/RigolOscilloscope) which was further developed by [@jeanyvesb9](https://github.com/jeanyvesb9/Rigol1000z).

I have heavily modified the work to be closer to a full implementation of a Rigol1000z library.

My goal for the rewrite has been to make the device as easy as possible to control by:
* Type hinting function parameters, and return values.
* Developing a command hierarchy as it is found in the Rigol programming manual and adding docstrings describing the effect of the function.
* Implementing most set/get commands as properties and related setters for a more organic device interface.
* Defining discrete string constants separately so that autocompletion of constants can be preformed from the corresponding enumeration class
