class ESource:
    D0 = "D0"
    D1 = "D1"
    D2 = "D2"
    D3 = "D3"
    D4 = "D4"
    D5 = "D5"
    D6 = "D6"
    D7 = "D7"
    D8 = "D8"
    D9 = "D9"
    D10 = "D10"
    D11 = "D11"
    D12 = "D12"
    D13 = "D13"
    D14 = "D14"
    D15 = "D15"

    Ch1 = "CHAN1"
    Ch2 = "CHAN2"
    Ch3 = "CHAN3"
    Ch4 = "CHAN4"

    Math = "MATH"


sources_digital = {
    ESource.D0,
    ESource.D1,
    ESource.D2,
    ESource.D3,
    ESource.D4,
    ESource.D5,
    ESource.D6,
    ESource.D7,
    ESource.D8,
    ESource.D9,
    ESource.D10,
    ESource.D11,
    ESource.D12,
    ESource.D13,
    ESource.D14,
    ESource.D15,
}

sources_analog = {
    ESource.Ch1,
    ESource.Ch2,
    ESource.Ch3,
    ESource.Ch4,
}

sources_math = {"MATH"}


class EWaveformMode:
    Normal = "NORM"
    Max = "MAX"
    Raw = "RAW"


waveform_modes = {EWaveformMode.Normal, EWaveformMode.Max, EWaveformMode.Raw}


class EWaveformReadFormat:
    Word = "WORD"
    Byte = "BYTE"
    Ascii = "ASC"


waveform_read_formats = {EWaveformReadFormat.Word, EWaveformReadFormat.Byte, EWaveformReadFormat.Ascii}
