from database import engine, Base
import models

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)