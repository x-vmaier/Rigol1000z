import os
import numpy as _np
import tqdm as _tqdm
import pyvisa as _visa
from Rigol1000z.commandmenu import CommandMenu
from Rigol1000z.commands import *


class Rigol1000z(CommandMenu):
    """
    Rigol DS1000z series oscilloscope driver.
    """

    def __init__(self, visa_resource: _visa.Resource):
        super().__init__(visa_resource)

        self.channels = [Channel(self.visa_resource, c) for c in range(1, 5)]

        # acquire must count enabled channels
        self.acquire = Acquire(self.visa_resource, self.channels)
        self.calibrate = Calibrate(self.visa_resource)

        self.cursor = Cursor(self.visa_resource)
        self.decoder = Decoder(self.visa_resource)
        self.display = Display(self.visa_resource)
        self.etable = Etable(self.visa_resource)
        self.function = Function(self.visa_resource)
        self.ieee488 = IEEE488(self.visa_resource)
        self.la = LA(self.visa_resource)
        self.lan = LAN(self.visa_resource)
        self.math = Math(self.visa_resource)
        self.mask = Mask(self.visa_resource)
        self.measure = Measure(self.visa_resource)
        self.reference = Reference(self.visa_resource)
        self.source = Source(self.visa_resource)
        self.storage = Storage(self.visa_resource)
        self.system = System(self.visa_resource)
        self.trace = Trace(self.visa_resource)
        self.timebase = Timebase(self.visa_resource)
        self.trigger = Trigger(self.visa_resource)
        self.waveform = Waveform(self.visa_resource)

        # self.trigger = _Rigol1000zTrigger(self)
        # self.timebase = _Rigol1000zTimebase(self)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.visa_resource.close()
        return False

    def __del__(self):
        self.visa_resource.close()

    def __getitem__(self, i):
        """
        Channels 1 through 4 (or 2 depending on the oscilloscope model) are accessed
        using `[channel_number]`.  e.g. osc[2] for channel 2.  Channel 1 corresponds
        to index 1 (not 0).

        :param i: Channel number to retrieve
        :return:
        """
        # assert i in {c.channel for c in self._channels}
        assert 1 <= i <= 4, 'Not a valid channel.'
        return self.channels[i - 1]

    def __len__(self):
        return len(self.channels)

    # region core commands

    def autoscale(self):
        self.visa_write(':aut')

    def clear(self):
        self.visa_write(':clear')

    def run(self):
        self.visa_write(':run')

    def stop(self):
        self.visa_write(':stop')

    def set_single_shot(self):
        self.visa_write(':sing')

    def force(self):
        self.visa_write(':tfor')

    # endregion

    def get_channels_enabled(self):
        return [c.enabled() for c in self.channels]

    # todo: make this more closely knit with the library
    def get_screenshot(self, filename=None, img_format='png'):
        """
        Downloads a screenshot from the oscilloscope.

        Args:
            filename (str): The name of the image file.  The appropriate
                extension should be included (i.e. jpg, png, bmp or tif).
            img_format (str): The format image that should be downloaded.  Options
                are 'jpeg, 'png', 'bmp8', 'bmp24' and 'tiff'.  It appears that
                'jpeg' takes <3sec to download while all the other formats take
                <0.5sec.  Default is 'png'.
        """

        assert img_format in ('jpeg', 'png', 'bmp8', 'bmp24', 'tiff')

        # Due to the up to 3s delay, we are setting timeout to None for this operation only
        old_timeout = self.visa_resource.timeout
        self.visa_resource.timeout = None

        raw_img = self.visa_ask_raw(':disp:data? on,off,%s' % img_format, 3850780)[11:-4]

        self.visa_resource.timeout = old_timeout

        if filename:
            try:
                os.remove(filename)
            except OSError:
                pass
            with open(filename, 'wb') as fs:
                fs.write(raw_img)

        return raw_img

    def get_data(self, mode=EWaveformMode.Normal, filename=None):
        """
        Download the captured voltage points from the oscilloscope.

        Args:
            mode (str): 'norm' if only the points on the screen should be
                downloaded, and 'raw' if all the points the ADC has captured
                should be downloaded.  Default is 'norm'.
            filename (None, str): Filename the data should be saved to.  Default
                is `None`; the data is not saved to a file.

        Returns:
            2-tuple: A tuple of two lists.  The first list is the time values
                and the second list is the voltage values.

        """
        assert mode in {EWaveformMode.Normal, EWaveformMode.Raw}

        # Setup scope
        self.stop()

        self.waveform.source = ESource.Ch1
        self.waveform.mode = mode
        self.waveform.read_format = EWaveformReadFormat.Byte

        # retrieve the data preable
        info: PreambleContext = self.waveform.data_premable

        print(f"info {info}")

        max_num_pts: int = 250000
        num_blocks: int = info.points // max_num_pts
        last_block_pts: int = info.points % max_num_pts

        datas = []
        for i in _tqdm.tqdm(range(num_blocks + 1), ncols=60):
            if i < num_blocks:
                self.waveform.read_start_point = 1 + i * 250000
                self.waveform.read_end_point = 250000 * (i + 1)
            else:
                if last_block_pts:
                    self.waveform.read_start_point = 1 + num_blocks * 250000
                    self.waveform.read_end_point = num_blocks * 250000 + last_block_pts
                else:
                    break
            data = self.visa_ask_raw(':wav:data?', 250000)

            with open(f"data_resp_raw{i}.csv", "wb") as f:
                print("writing")
                f.write(data)

            # Get the response length from the header data
            # data_response_len_bytes = int("".join(chr(c) for c in data[2:11]))
            # print(f"header resp length={data_response_len_bytes}")

            data = _np.frombuffer(data[11:-1], 'B')  # Last byte marks the end of the message.
            datas.append(data)

        datas = _np.concatenate(datas)
        v = (datas - info.y_origin - info.y_reference) * info.y_increment
        t = _np.arange(0, info.points * info.x_increment, info.x_increment)

        if filename:
            print(filename)
            try:
                os.remove(filename)
            except OSError:
                pass
            _np.savetxt(filename, _np.c_[t, v], '%.12e', ', ', '\n')

        return t, v
