from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from .database import Base, engine

class UserTable(SQLAlchemyBaseUserTableUUID, Base):
    pass



