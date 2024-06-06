from pydantic import BaseModel

class AthenaQuery(BaseModel):
    query: str
    database: str
