class Heatsink:
    def __init__(self, material: str, heatpipes: int, dissipation_watts: int):
        self.material = material
        self.heatpipes = heatpipes
        self.dissipation_watts = dissipation_watts

    def can_dissipate(self, tdp_watts: int) -> bool:
        return self.dissipation_watts >= tdp_watts
