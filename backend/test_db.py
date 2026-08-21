from app.database import engine
from sqlalchemy import text


with engine.connect() as connection:

    result = connection.execute(
        text("SELECT current_database()")
    )

    print("Database:", result.scalar())