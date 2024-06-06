from enum import Enum

class FileType(str, Enum):
    EXCEL = "excel"
    PARQUET = "parquet"

class FileData:
    def __init__(self, file_type: FileType, file_name: str, data: dict):
        self.file_type = file_type
        self.file_name = file_name
        self.data = data
