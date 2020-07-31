import os
import numpy as _np
import tqdm as _tqdm
import pyvisa as _visa
from Rigol1000z.commandmenu import CommandMenu
from Rigol1000z.constants import *
from typing import List, Union


class Channel(CommandMenu):
    """
    Complete
    """

    def __init__(self, visa_resource: _visa.Resource, channel: int):
        super().__init__(visa_resource)
        self._channel = channel

        self.cmd_hierarchy_str = f":chan{self._channel}"

    @property
    def channel(self):
        return self._channel

    @property
    def bw_limit_20mhz(self):
        resp = self.visa_ask(':bwl?')
        return resp == "20M"

    @bw_limit_20mhz.setter
    def bw_limit_20mhz(self, val: bool):
        self.visa_write(f':bwl {"20M" if val else "OFF"}')

    @property
    def coupling(self):
        return self.visa_ask(':coup?')

    @coupling.setter
    def coupling(self, val):
        val = val.upper()
        assert val in ('AC', 'DC', 'GND')
        self.visa_write(f':coup {val}')

    @property
    def enabled(self):
        return bool(int(self.visa_ask(':disp?')))

    @enabled.setter
    def enabled(self, val: bool):
        self.visa_write(f':disp {int(val is True)}')

    @property
    def invert(self):
        return bool(int(self.visa_ask(':inv?')))

    @invert.setter
    def invert(self, val: bool):
        self.visa_write(f':inv {int(val is True)}')

    @property
    def offset_v(self) -> float:
        return float(self.visa_ask(':off?'))

    @offset_v.setter
    def offset_v(self, val: float):
        """
        Related to the current vertical scale and probe ratio

        When the probe ratio is 1X:
            vertical scale≥500mV/div: -100V to +100V
            vertical scale<500mV/div: -2V to +2V
        When the probe ratio is 10X:
            vertical scale≥5V/div: -1000V to +1000V
            vertical scale<5V/div: -20V to +20V

        :param val: The offset voltage to set (volts)
        """
        # todo: check probe ratio and vertical scale to ensure valid value

        assert -1000. <= val <= 1000.
        self.visa_write(f':off {val:.4e}')

    @property
    def range_v(self) -> float:
        return float(self.visa_ask(':rang?'))

    @range_v.setter
    def range_v(self, val: float):
        assert 8e-3 <= val <= 800.
        self.visa_write(f':rang {val:.4e}')

    @property
    def calibration_delay(self) -> float:
        """
        Query the delay calibration time of the specified channel to calibrate the zero offset
        of the corresponding channel. The default unit is s.

        :return:
        """
        return float(self.visa_ask(':tcal?'))

    @calibration_delay.setter
    def calibration_delay(self, val: float):
        """
        Can only be set to the specific values in the specified step. If the parameter you
        sent is not one of the specific values, the parameter will be set to the nearest specific
        values automatically

        :param val:
        :return:
        """
        # todo: add addition rules to detect and ensure that channel can't leave the specified delay range

        assert -100e-9 <= val <= 100e-9
        self.visa_write(f':tcal {val:.4e}')

    @property
    def scale_v(self):
        return float(self.visa_ask(':scal?'))

    @scale_v.setter
    def scale_v(self, val):
        probe_ratio = self.probe_ratio
        assert 1e-3 * probe_ratio <= val <= 10. * probe_ratio
        self.visa_write(f':scal {val:.4e}')

    @property
    def probe_ratio(self) -> float:
        return float(self.visa_ask(':prob?'))

    @probe_ratio.setter
    def probe_ratio(self, val: float):
        assert val in {0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50, 100, 200, 500, 1000}
        self.visa_write(f':prob {val:.4e}')

    @property
    def units(self) -> str:
        return self.visa_ask(':unit?')

    @units.setter
    def units(self, val: str):
        val = val.lower()
        assert val in ('volt', 'watt', 'amp', 'unkn')
        self.visa_write(f':unit {val}')

    @property
    def vernier(self):
        return bool(int(self.visa_ask(':vern?')))

    @vernier.setter
    def vernier(self, val: bool):
        self.visa_write(f':vern {int(val is True)}')


# incomplete
class Acquire(CommandMenu):
    cmd_hierarchy_str = ":acq"

    def __init__(self, visa_resource: _visa.Resource, channels: List[Channel]):
        super().__init__(visa_resource)
        self._linked_channels = channels

    @property
    def averages(self):
        """
        Query the number of averages under the average acquisition mode.
        2^n (n is an integer from 1 to 10)
        :return: an integer between 2 and 1024.
        """
        return int(self.visa_ask(':aver?'))

    @averages.setter
    def averages(self, val):
        """
        Set the number of averages under the average acquisition mode.

        :param val:
        :return:
        """
        assert val in [2 ** n for n in range(1, 11)]
        self.visa_write(f':aver {int(val)}')

    @property
    def memory_depth(self) -> int:
        """
        Query the memory depth of the oscilloscope (namely the number of waveform
        points that can be stored in a single trigger sample). The default unit is pts (points).

        Auto mode is indicated with a -1 returned

        :return:
        """
        md = self.visa_ask(':mdep?')
        return int(md) if md != 'AUTO' else -1

    # todo: requires access to channels
    @memory_depth.setter
    def memory_depth(self, val: int):
        """
        #todo: figure out if this command requires a run command before memory depth can be written

        Auto mode is indicated with a -1

        :param val: The number of points to acquire
        :return:
        """

        num_enabled_chans = sum(1 if c.enabled else 0 for c in self._linked_channels)

        val = int(val) if val != -1 else 'AUTO'

        if num_enabled_chans == 1:
            assert val in ('AUTO', 12000, 120000, 1200000, 12000000, 24000000)
        elif num_enabled_chans == 2:
            assert val in ('AUTO', 6000, 60000, 600000, 6000000, 12000000)
        elif num_enabled_chans in (3, 4):
            assert val in ('AUTO', 3000, 30000, 300000, 3000000, 6000000)

        # todo: set to run mode perhaps
        self.visa_write(f':mdep {val}')

    @property
    def mode(self):
        return self.visa_ask(':type?')

    @mode.setter
    def mode(self, val: str):
        assert val in {EAcquireModes.Normal, EAcquireModes.Averages, EAcquireModes.HighResolution, EAcquireModes.Peak}
        self.visa_write(f':type {val}')

    @property
    def sampling_rate(self):
        """
        Sample rate is the sample frequency of the oscilloscope, namely the waveform points sampled per second.

        The following equation describes the relationship among memory depth, sample rate, and waveform length:
            Memory Depth = Sample Rate x Waveform Length

        Wherein:
            Memory Depth can be set using the :ACQuire:MDEPth command
            Waveform Length is the product of:
                The horizontal timebase (set by the :TIMebase[:MAIN]:SCALe command)
                The number of the horizontal scales (12 for DS1000Z).

        :return: A float with units Sa/s
        """
        return float(self.visa_ask(':srat?'))


class Calibrate(CommandMenu):
    """
    Complete
    """

    cmd_hierarchy_str = ":cal"

    def set_auto_calibration(self, state: bool = True):
        self.visa_write(f":{'star' if state else 'quit'}")


# incomplete
class Cursor(CommandMenu):
    cmd_hierarchy_str = ":curs"


# incomplete
class Decoder(CommandMenu):
    cmd_hierarchy_str = ":dec"


# incomplete
class Display(CommandMenu):
    cmd_hierarchy_str = ":disp"

    def clear(self):
        return self.visa_write(':cle')

    # def data
    # this is currently implemented in the primary Rigol1000z class

    @property
    def mode(self):
        return self.visa_ask(':type?')

    @mode.setter
    def mode(self, val: str):
        assert val in {EDisplayModes.Vectors, EDisplayModes.Dots}
        self.visa_write(f':type {val}')

    @property
    def persistence_time(self):
        return self.visa_ask(':grad:time?')

    @persistence_time.setter
    def persistence_time(self, val: Union[float, str]):
        """
         MIN: set the persistence time to its minimum to view the waveform changing in high refresh rate.

         Specific Values: set the persistence time to one of the values listed above to observe
        glitch that changes relatively slowly or glitch with low occurrence probability.

         INFinite: in this mode, the oscilloscope displays the newly acquired waveform
        without clearing the waveform formerly acquired. It can be used to measure noise
        and jitter as well as capture incidental events.

        :param val:
        :return:
        """
        assert val in {"MIN", 0.1, 0.2, 0.5, 1, 5, 10, "INF"}
        self.visa_write(f':grad:time {val}')

    @property
    def brightness(self):
        """
        Query the screen brightness

        :return: A float between 0 and 1
        """
        return float(self.visa_ask(':WBR?') / 100.0)

    @brightness.setter
    def brightness(self, val: float):
        """
        Set the screen brightness

        :param val: A float between 0 and 1
        :return:
        """
        assert 0.0 <= val <= 1.0
        self.visa_write(f':WBR {int(val * 100)}')

    @property
    def grid(self):
        """
        Set or query the grid type of screen display
        :return:
        """
        return self.visa_ask(':GRID?')

    @grid.setter
    def grid(self, val: float):
        assert val in {EDisplayGrid.Full, EDisplayGrid.Half, EDisplayGrid.NoGrid}
        self.visa_write(f':GRID {val}')


# incomplete
class Etable(CommandMenu):
    cmd_hierarchy_str = ":etabl"


# incomplete
class Function(CommandMenu):
    cmd_hierarchy_str = ":func"


class IEEE488(CommandMenu):
    """
    Complete
    """
    cmd_hierarchy_str = "*"

    def clear_event_registers(self) -> None:
        """
        Clear all the event registers and clear the error queue.
        """
        self.visa_ask("cls")

    @property
    def event_register_enable_mask(self) -> int:
        """
        Query the enable register for the standard event status register set.
        """
        return int(self.visa_ask("ese?"))

    @event_register_enable_mask.setter
    def event_register_enable_mask(self, val: int):
        """
        Set the enable register for the standard event status register set.
        """
        assert 0 <= val < 256
        self.visa_write(f"ese {val}")

    def query_and_clear_event_register(self) -> int:
        """
        Query and clear the event register for the standard event status register.
        """
        return int(self.visa_ask("esr?"))

    @property
    def id_string(self) -> str:
        return self.visa_ask('idn?')

    @property
    def operation_complete(self) -> bool:
        return bool(int(self.visa_ask('opc?')))

    def reset(self) -> None:
        """
        Restore the instrument to the default state.
        """
        self.visa_write("rst")

    @property
    def status_register_enable_mask(self) -> int:
        """
        Query the enable register for the status byte register set.
        """
        return int(self.visa_ask("sre?"))

    @status_register_enable_mask.setter
    def status_register_enable_mask(self, val: int):
        """
        Set the enable register for the status byte register set.
        """
        assert 0 <= val < 256
        self.visa_write(f"sre {val}")

    def query_and_clear_status_register(self) -> int:
        """
        Query the event register for the status byte register.
        The value of the status byte register is set to 0 after this command is executed.
        """
        return int(self.visa_ask("stb?"))

    def self_test(self) -> int:
        """
        Perform a self-test and then return the self-test results
        """
        return int(self.visa_ask("tst?"))

    def wait_until_command_completion(self) -> int:
        """
        Wait for the operation to finish.
        The subsequent command can only be carried out after the
        current command has been executed.
        """
        return int(self.visa_ask("wai"))


# incomplete
class LA(CommandMenu):
    cmd_hierarchy_str = ":la"


# incomplete
class LAN(CommandMenu):
    cmd_hierarchy_str = ":lan"


# incomplete
class Math(CommandMenu):
    cmd_hierarchy_str = ":math"


# incomplete
class Mask(CommandMenu):
    cmd_hierarchy_str = ":mask"


# incomplete
class Measure(CommandMenu):
    cmd_hierarchy_str = ":meas"

    @property
    def source(self):
        self.visa_ask(f':sour?')
        return self._osc.selected_channel()

    def get_voltage_rms_v(self):
        assert 1 <= self._channel <= 4, 'Invalid channel.'
        return self.visa_ask(f':ITEM? VRMS,CHAN{self._channel}')

    def channel_selected(self):
        self._osc.write(f':SOUR CHAN{self._channel}')
        return self._osc.selected_channel()

    def selected_channel(self):
        return self.visa_ask(':MEAS:SOUR?')


# incomplete
class Reference(CommandMenu):
    cmd_hierarchy_str = ":meas"


# incomplete
class Source(CommandMenu):
    cmd_hierarchy_str = ":meas"


# incomplete
class Storage(CommandMenu):
    cmd_hierarchy_str = ":meas"


# incomplete
class System(CommandMenu):
    cmd_hierarchy_str = ":meas"


# incomplete
class Trace(CommandMenu):
    cmd_hierarchy_str = ":meas"


class TimebaseDelay(CommandMenu):
    cmd_hierarchy_str = ":tim:del"

    @property
    def enabled(self) -> bool:
        return bool(int(self.visa_ask(':enab?')))

    @enabled.setter
    def enabled(self, val: bool):
        self.visa_write(f':enab {val}')

    @property
    def offset(self) -> float:
        """
        Query the delayed timebase offset. The default unit is s.

        :return:
        """
        return float(self.visa_ask(':offs?'))

    @offset.setter
    def offset(self, val: float):
        """
        Honestly don't know what this does. Read the documentation for more info


        Set the delayed timebase offset. The default unit is s.
        -(LeftTime - DelayRange/2) to (RightTime - DelayRange/2)

        LeftTime = 6 x MainScale - MainOffset
        RightTime = 6 x MainScale + MainOffset
        DelayRange = 12 x DelayScale
        Wherein, MainScale is the current main timebase scale of the oscilloscope,
        MainOffset is the current main timebase offset of the oscilloscope, and DelayScale is
        the current delayed timebase scale of the oscilloscope.

        :param val:
        :return:
        """
        assert val

        self.visa_write(f':offs {val}')


class Timebase(CommandMenu):
    cmd_hierarchy_str = ":tim"

    def __init__(self, visa_resource):
        super().__init__(visa_resource)
        self.delay = TimebaseDelay(visa_resource)

    @property
    def timebase_scale_s_div(self):
        return float(self.visa_ask(':scal?'))

    def timebase_scale_s_div(self, timebase):
        assert 50e-9 <= timebase <= 50
        self.visa_write(f':scal {timebase:.4e}')

    @property
    def timebase_mode(self) -> str:
        return self.visa_ask(':mode?')

    @timebase_mode.setter
    def timebase_mode(self, val: str):
        val = val.lower()
        assert val in ('main', 'xy', 'roll')
        self.visa_write(f':mode {val}')

    @property
    def timebase_offset_s(self):
        return self.visa_ask(':offs?')

    @timebase_offset_s.setter
    def timebase_offset_s(self, val):
        self.visa_write(f':offs {-val:.4e}')


# incomplete
class TriggerEdge(CommandMenu):
    cmd_hierarchy_str = ":trig:edg"

    @property
    def trigger_level_v(self):
        return self.visa_ask(':lev?')

    @trigger_level_v.setter
    def trigger_level_v(self, level):
        self.visa_write(f':lev {level:.3e}')


# incomplete
class Trigger(CommandMenu):
    cmd_hierarchy_str = ":trig"

    def __init__(self, visa_resource):
        super().__init__(visa_resource)
        self.edge = TriggerEdge(visa_resource)

    @property
    def trigger_holdoff_s(self):
        return self.visa_ask(':hold?')

    @trigger_holdoff_s.setter
    def trigger_holdoff_s(self, holdoff):
        self.visa_write(':hold %.3e' % holdoff)
        return self.get_trigger_holdoff_s()


class PreambleContext:
    """
    Proper storage class for preamble data
    """

    def __init__(self, preamble_str):
        pre = preamble_str.split(',')

        self.format: int = int(pre[0])
        self.type: int = int(pre[1])
        self.points: int = int(pre[2])
        self.count: int = int(pre[3])
        self.x_increment: float = float(pre[4])
        self.x_origin: float = float(pre[5])
        self.x_reference: float = float(pre[6])
        self.y_increment: float = float(pre[7])
        self.y_origin: float = float(pre[8])
        self.y_reference: float = float(pre[9])


class Waveform(CommandMenu):
    """
    Complete
    """
    cmd_hierarchy_str = ":wav"

    @property
    def source(self) -> str:
        return self.visa_ask(':sour?')

    @source.setter
    def source(self, val: str):
        assert val in {*sources_analog, *sources_digital, *sources_math}
        self.visa_write(f':sour {val}')

    @property
    def mode(self) -> str:
        return self.visa_ask(':mode?')

    @mode.setter
    def mode(self, val: str):
        assert val in waveform_modes
        self.visa_write(f':mode {val}')

    @property
    def read_format(self) -> str:
        return self.visa_ask(':form?')

    @read_format.setter
    def read_format(self, val: str):
        assert val in waveform_read_formats
        self.visa_write(f':form {val}')

    @property
    def x_increment(self) -> float:
        """
        Query the time difference between two neighboring points
        of the specified channel source in the X direction.

        In NORMal mode:
            XINCrement = TimeScale/100.

        In RAW mode:
            XINCrement = 1/SampleRate.

        In MAX mode:
            XINCrement = TimeScale/100 when the instrument is in running status;
            XINCrement = 1/SampleRate when the instrument is in stop status.

        :return:
        """
        return float(self.visa_ask(':xinc?'))

    @property
    def y_increment(self) -> float:
        """
        Query the waveform increment of the specified channel source in the Y direction.
        The unit is the same as the current amplitude unit.

        The return value is related to the current data reading mode:
            In NORMal mode:
                YINCrement = VerticalScale/25

            In RAW mode:
                YINCrement is related to the Verticalscale of the internal waveform
                and the Verticalscale currently selected.

            In MAX mode:
                Instrument is in running status:
                    YINCrement = VerticalScale/25

                Instrument is in stop status:
                    YINCrement is related to the Verticalscale of the internal waveform and the Verticalscale
                    currently selected.

        :return:
        """
        return float(self.visa_ask(':yinc?'))

    @property
    def x_origin(self) -> float:
        """
        Query the start time of the waveform data of the channel source currently selected in the
        X direction.

        The return value is related to the current data reading mode:
            In NORMal mode:
                The query returns the start time of the waveform data displayed on the screen.
            In RAW mode:
                The query returns the start time of the waveform data in the internal memory.
            In MAX mode:
                the query returns the start time of the waveform data displayed on the
                screen when the instrument is in running status; the query returns the start time of
                the waveform data in the internal memory when the instrument is in stop status.

        :return:
        """
        return float(self.visa_ask(':xor?'))

    @property
    def y_origin(self) -> int:
        """
        Query the vertical offset relative to the vertical reference position of the specified channel
        source in the Y direction.

        The return value is related to the current data reading mode:
            In NORMal mode:
                YORigin = VerticalOffset/YINCrement.

            In RAW mode:
                YORigin is related to the Verticalscale of the internal waveform and the Verticalscale selected.

            In MAX mode:
                Instrument in running status:
                    YORigin = VerticalOffset/YINCrement
                Instrument in stop status:
                    YORigin is related to the Verticalscale of the internal waveform and the Verticalscale selected

        :return:
        """
        return int(self.visa_ask(':yor?'))

    @property
    def x_reference(self) -> int:
        """
        Query the reference time of the specified channel source in the X direction.

        The query returns 0 (namely the first point on the screen or in the internal memory)

        :return:
        """
        return int(self.visa_ask(':xref?'))

    @property
    def y_reference(self) -> int:
        """
        Query the vertical reference position of the specified channel source in the Y direction

        YREFerence is always 127 (the screen bottom is 0 and the screen top is 255).

        :return:
        """
        return int(self.visa_ask(':yref?'))

    @property
    def read_start_point(self):
        """
        Query the start point of waveform data reading.
        :return:
        """
        return int(self.visa_ask(':star?'))

    @read_start_point.setter
    def read_start_point(self, val: int):
        """
        Set the start point of waveform data reading.
        :param val:
        :return:
        """
        self.visa_write(f':star {val}')

    @property
    def read_end_point(self):
        """
        Query the stop point of waveform data reading.
        :return:
        """
        return int(self.visa_ask(':stop?'))

    @read_end_point.setter
    def read_end_point(self, val: int):
        """
        Set the stop point of waveform data reading.
        :param val:
        :return:
        """
        self.visa_write(f':stop {val}')

    @property
    def data_premable(self) -> PreambleContext:
        """
        Get information about oscilloscope axes.
        """
        raw_pre = self.visa_ask(':pre?')
        return PreambleContext(raw_pre)

    # todo: review get is data handled directly from the Rigol class.
    #  Make sure this makes sense because this violates the pattern taken by the rest of the menus
