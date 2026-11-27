class NetworkInterface:
    def __init__(self, interface_name: str, mac_address: str, link_speed_mbps: int = 1000):
        self.interface_name = interface_name
        self.mac_address = mac_address
        self.link_speed_mbps = link_speed_mbps
        self.link_up: bool = False

    def bring_up(self) -> bool:
        self.link_up = True
        return True

    def bring_down(self) -> bool:
        self.link_up = False
        return False
