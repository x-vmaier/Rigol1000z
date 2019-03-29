# Rigol1000z
Python library to control Rigol DS1000z series oscilloscopes based on the VISA protocol (PyVISA). The oscilloscope can be connected either by USB or by Ethernet to the local network (See PyVISA docs for more information).

Tested on Windows 10 and Arch Linux using a Rigol DS1054Z.

## Dependencies
* [numpy](https://github.com/numpy/numpy)
* [pyvisa](https://github.com/pyvisa/pyvisa)
* [tqdm](https://github.com/tqdm/tqdm)

## Example
```python
import visa
import Rigol1000z

rm = visa.ResourceManager()

# We are connecting the oscilloscope through USB here.
# Only one VISA-compatible instrument is connected to our computer,
# thus the first resource on the list is our oscilloscope.
# You can see all connected and available local devices calling
#
# print(rm.list_resources())
#
osc_resource = rm.open_resource(rm.list_resources()[0])

osc = Rigol1000z.Rigol1000z(osc_resource)

# Change voltage range of channel 1 to 50mV/div.
osc[1].set_vertical_scale_V_div(50e-3)

# Stop the scope.
osc.stop()

# Take a screenshot.
osc.get_screenshot('screenshot.png', 'png')

# Capture the data sets from channels 1--4 and
# write the data sets to their own file.
for c in range(1,5):
    osc[c].get_data('raw', 'channel%i.dat' % c)
```

## Calling aditional commands
This library implements function interfaces to some of the most used SCPI commands available in the Rigol DS1000z series oscilloscopes. However, many more commands are available in the 'MSO1000z/DSO1000z Programming Guide' (http://int.rigol.com/File/TechDoc/20151218/MSO1000Z&DS1000Z_ProgrammingGuide_EN.pdf). I have not verified it, but it's probable that all options available in the physical and on-screen menus have corresponding SCPI commands. Users can send SCPI commands and receive information directly from the oscilloscope through the following methods:

```python
visa_write(cmd)

# Will read all bytes in the buffer until a termination character is found, 
# and interpret them as ASCII characters
visa_read()

# Will read num_bytes bytes in the buffer, or until a termination caracter is found if
# num_bytes == -1, and hand them out as binary information
visa_read_raw(num_bytes=-1):

# Combines the functions of visa_write(cmd) and visa_read()
visa_ask(cmd):

# Combines the functions of visa_write(cmd) and visa_read_raw()
visa_ask_raw(cmd, num_bytes=-1)
```

### Reading software measurements and statical data

Due to the many possible combinations routines to receive statistics and measurements data are not preprogrammed, and have to be implemented by the user by using the direct VISA communication functions. For example:

```python
# Select channel 1 as an input to the hardware frequency counter
scope.visa_write(':MEASure:COUNter:SOURce CHANnel1')

# Turn on statistics display
scope.visa_write(':MEASure:STATistic:DISPlay ON')
# Change statistics mode to 'difference'
scope.visa_write(':MEASure:STATistic:MODE DIFFerence')


# We can have up to five different measurementes displayed
# on the oscilloscope screen at the same time

# Select Vpp measurement on channel 1 to be displayed
scope.visa_write(':MEASure:STATistic:ITEM VPP,CHANnel1')
# Select Vpp measurement on channel 2 to be displayed
scope.visa_write(':MEASure:STATistic:ITEM VPP,CHANnel2')
# Select Rising Edge Delay measurement between channel 1 and
# channel 2 to be displayed
scope.visa_write(':MEASure:STATistic:ITEM RDELay,CHANnel1,CHANnel2')

# Clear the statistical results in memory
scope.visa_write(':MEASure:STATistic:RESet')


# We can read the statistical results (averages, maximums, minimums, deviations, etc.)
# or the current values of the measurements enabled above.
# Numeric results are given in ASCII scientific notation, so a quick conversion
# to float is needed

vin = float(scope.visa_ask(':MEASure:STATistic:ITEM? AVERages,VPP,CHANnel1'))
vout = float(scope.visa_ask(':MEASure:STATistic:ITEM? AVERages,VPP,CHANnel2'))
delay = float(scope.visa_ask(':MEASure:STATistic:ITEM? AVERages,RDELay'))
freq = float(scope.visa_ask(':MEASure:COUNter:VALue?'))
```

An full implementation of a manual frequency sweep bode plot measurement is available in the _examples_ folder.


## Acknowledgements
Based on the original work by @jtambasco. I have done a code cleanup, a couple of bug fixes and a complete rewrite of the backend, now with a PyVISA dependency in order to make this library cross-platform. Also improved documentation and added examples.
