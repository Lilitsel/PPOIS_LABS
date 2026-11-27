class DisplayPipeline:
    def __init__(self, vsync_enabled: bool = True, hdr_enabled: bool = False):
        self.vsync_enabled = vsync_enabled
        self.hdr_enabled = hdr_enabled

    def enable_hdr(self) -> bool:
        self.hdr_enabled = True
        return True
