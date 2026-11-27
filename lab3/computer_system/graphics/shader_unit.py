class ShaderUnit:
    def __init__(self, unit_id: int, shader_version: str = "SM 6.7"):
        self.unit_id = unit_id
        self.shader_version = shader_version
        self.compiled_shaders: int = 0

    def compile_shader(self, name: str) -> int:
        if name.strip():
            self.compiled_shaders += 1
        return self.compiled_shaders
