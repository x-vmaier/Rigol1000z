# Rigol1000z
Python library to control Rigol DS1000z series oscilloscopes based on the VISA protocol (PyVISA). The oscilloscope can be connected either by USB or by Ethernet to the local network (See PyVISA docs for more information).

## Platforms
* Windows 10 - Tested
* ArchLinux - when forked, [@jeanyvesb9](https://github.com/jeanyvesb9/Rigol1000z) said his version worked so I suspect compatibility.

## Dependencies
* [python3.7](https://www.python.org/downloads/release)+ Python version as f-strings are used in the library
* [numpy](https://github.com/numpy/numpy) Library for efficient storage and processing of arrays
* [pyvisa](https://github.com/pyvisa/pyvisa) Visa communication protocol
* [tqdm](https://github.com/tqdm/tqdm) Command line progress bar

## Recommended
* [pipenv](https://pypi.org/project/pipenv/)
makes installation of requirements easier and separates python environments reducing the probability of package dependency conflicts.
To install run the following commands from your working directory 

```python
$ pip install pipenv
$ pipenv install
```

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
