class CaseChassis:
    def __init__(self, form_factor: str, fan_mounts: int = 6, front_usb_ports: int = 2):
        self.form_factor = form_factor
        self.fan_mounts = fan_mounts
        self.front_usb_ports = front_usb_ports
        self.panel_closed: bool = True

    def open_side_panel(self) -> bool:
        self.panel_closed = False
        return False

    def close_side_panel(self) -> bool:
        self.panel_closed = True
        return True
