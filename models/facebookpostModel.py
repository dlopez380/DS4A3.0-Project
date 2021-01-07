from sqlalchemy import Column, String, Integer, Numeric
# from sqlalchemy.orm import relationship
from mannagers.dbmannager import Base, session

class Facebookpost(Base):
	__tablename__ = 'facebookpost'
	id=Column(Integer, primary_key=True)
	facebookpage=Column('facebookpage', String)
	postid=Column('postid', String)
	text=Column('text', String)
	date=Column('date', String)
	shares=Column('shares', Numeric)
	totalComments=Column('totalComments', Numeric)
	like = Column('like', String)
	love = Column('love', String)
	wow = Column('wow', String)
	haha = Column('haha', String)
	sorry = Column('sorry', String)
	angry = Column('angry', String)
	care = Column('care', String)
	totalreactions = Column('totalreactions', String)
	# facebookcomments = relationship("Facebookcomment", backref="facebookpost")
	
	def all(self):
		response = session.query(Facebookpost).all()
		return response

	def getByPostid(self, postid=False):
		queryResult = session.query(Facebookpost).filter(Facebookpost.postid == postid).all()
		if len(queryResult)>0:
			response = queryResult[0]
		else:
			response = False
		return response

	def save(self):
		session.add(self)
		session.commit()
		session.close()
		return self

	def update(self, data):
		dataCopy = {}
		for i in data:
			if len(str(data[i]))>0:
				dataCopy[i] = data[i]

		del dataCopy['featuredComments']
		session.query(Facebookpost).filter(Facebookpost.id == data['id']).update(dataCopy)
		session.commit()
		session.close()
		return data['id']

	def patch(self, data):
		self.facebookpage = data.get('facebookpage')
		self.postid = data.get('postid')
		self.text = data.get('text')
		self.date = data.get('date')
		self.shares = int(data.get('shares'))
		self.totalComments = int(data.get('totalComments'))
		self.like = data.get('like')
		self.love = data.get('love')
		self.wow = data.get('wow')
		self.haha = data.get('haha')
		self.sorry = data.get('sorry')
		self.angry = data.get('angry')
		self.care = data.get('care')
		self.totalreactions = data.get('totalreactions')
		return self