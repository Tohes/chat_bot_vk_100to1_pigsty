from sqlalchemy import MetaData
from sqlalchemy.orm import declarative_base

metadata = MetaData()
db = declarative_base(metadata)
