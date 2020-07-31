import pyvisa as _visa


class CommandMenu:
    """
    This class defines a visa menu hierarchy and interfaces to call commands from
    Adds a common pre-command branch string in order to ease writing of menus
    """
    cmd_hierarchy_str: str = ""

    def __init__(self, visa_resource: _visa.Resource):
        self.visa_resource: _visa.Resource = visa_resource

    @property
    def osc_model(self):
        idn: str = self.visa_resource.query("*IDN?")
        brand, model, serial_number, software_version, *add_args = idn.split(",")
        return model

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
