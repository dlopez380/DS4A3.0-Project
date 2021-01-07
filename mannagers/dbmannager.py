from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
# Connection and Base class for entities definitions
engine=create_engine('postgresql://scrapping:scrapping@localhost:5433/facebook', pool_size=10, max_overflow=5)
Base = declarative_base()
# Preconfigured session class
SessionMaker = sessionmaker(bind=engine)
# Generate database schema
Base.metadata.create_all(engine)
# Create a session
session = SessionMaker(expire_on_commit=False)

# class OrmAccess(object):
# 	def __init__(self, engine, Base, SessionMaker, session):
# 		self.engine = create_engine('postgresql://scrapping:scrapping@localhost:5433/facebook', pool_size=10, max_overflow=5)
# 		self.Base = declarative_base()
# 		self.Base.metadata.create_all(self.engine)
# 		self.SessionMaker = sessionmaker(bind=engine)
# 		self.session = session = SessionMaker()

#r = engine.connect().execute(text("SELECT 'Hello world';"))
#for i in r:
#   print(i)