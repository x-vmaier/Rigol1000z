import pyvisa as _visa
from Rigol1000z.constants import *


class CommandMenu:
    """
    This class defines a visa menu hierarchy and interfaces to call commands from
    Adds a common pre-command branch string in order to ease writing of menus
    """

    cmd_hierarchy_str: str = ""

    def __init__(self, visa_resource: _visa.Resource):
        self.visa_resource: _visa.Resource = visa_resource

    def visa_write(self, cmd):
        self.visa_resource.write(self.cmd_hierarchy_str + cmd)

    def visa_read(self):
        return self.visa_resource.read().strip()

    def visa_read_raw(self, num_bytes=-1):
        return self.visa_resource.read_raw(num_bytes)

    def visa_ask(self, cmd):
        return self.visa_resource.query(self.cmd_hierarchy_str + cmd)

    def visa_ask_raw(self, cmd, num_bytes=-1):
        self.visa_write(self.cmd_hierarchy_str + cmd)
        return self.visa_read_raw(num_bytes)


class Rigol1000zCommandMenu(CommandMenu):
    """
    Adds additional checks and features exclusive to the Rigol1000z series of scopes
    """

    def __init__(self, visa_resource, idn: str = None):
        super().__init__(visa_resource)

        if (idn is not None) and (type(idn) is str):
            self._idn_cache: str = idn

        else:
            # Cache the device's identifier
            self._idn_cache: str = self.visa_resource.query("*IDN?")

    @property
    def osc_model(self) -> str:
        brand, model, serial_number, software_version, *additional_args = self._idn_cache.split(",")
        return model

    @property
    def has_digital(self) -> bool:
        """
        Return whether the model has digital channels

        :return:
        """
        # Plus models supports digital channels
        return self.osc_model in {
            ScopeModel.DS1104Z_S_Plus, ScopeModel.DS1074Z_S_Plus,
            ScopeModel.DS1104Z_Plus, ScopeModel.DS1074Z_Plus}

    @staticmethod
    def source_valid(source: str, digital_valid: bool, ch_valid: bool, math_valid: bool) -> bool:
        if digital_valid and source in sources_digital:
            return True
        elif ch_valid and source in sources_analog:
            return True
        elif math_valid and source in sources_math:
            return True

        # If source any other value
        return False

    def get_rated_frequency(self) -> float:
        osc_model = self.osc_model

        if osc_model in {ScopeModel.DS1104Z_S_Plus, ScopeModel.DS1104Z_Plus}:
            return 100.0 * 10 ** 6  # 100MHz
        elif osc_model in {ScopeModel.DS1074Z_S_Plus, ScopeModel.DS1074Z_Plus}:
            return 70.0 * 10 ** 6  # 70MHz
        elif osc_model in {ScopeModel.DS1054Z}:
            return 50.0 * 10 ** 6  # 50MHz
        elif osc_model in {ScopeModel.DS1104Z}:
            print("You cheeky bastard")
            return 50.0 * 10 ** 6  # 50MHz
        else:
            raise ValueError(f"Invalid model: {osc_model}")
