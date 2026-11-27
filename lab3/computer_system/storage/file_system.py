from computer_system.storage.partition import Partition


class FileSystem:
    def __init__(self, fs_type: str, partition: Partition):
        self.fs_type = fs_type
        self.partition = partition
        self.files: dict[str, int] = {}

    def create_file(self, path: str, size_gb: int) -> bool:
        if size_gb <= self.partition.free_space_gb():
            self.partition.allocate_space(size_gb)
            self.files[path] = size_gb
            return True
        return False

    def delete_file(self, path: str) -> bool:
        if path in self.files:
            sz = self.files.pop(path)
            self.partition.used_gb = max(0, self.partition.used_gb - sz)
            return True
        return False
