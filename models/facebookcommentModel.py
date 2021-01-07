from sqlalchemy import Column, String, Integer, Numeric, ForeignKey
# from sqlalchemy.orm import relationship
from mannagers.dbmannager import Base, session

class Facebookcomment(Base):
	__tablename__ = 'facebookcomment'
	id=Column(Integer, primary_key=True)
	commentid=Column('commentid', String)
	postid=Column(String, ForeignKey('facebookpost.id'))
	text=Column('text', String)
	date=Column('date', String)
	commenter=Column('commenter', String)
	# post = relationship("Facebookpost", backref="facebookcomment")
	
	def all(self):
		response = session.query(Facebookcomment).all()
		return response

	def getByCommentId(self, commentid=False):
		queryResult = session.query(Facebookcomment).filter(Facebookcomment.commentid == commentid).all()
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
		session.query(Facebookcomment).filter(Facebookcomment.id == data['id']).update(dataCopy)
		session.commit()
		session.close()
		return data['id']

	def patch(self, data):
		self.commentid = data.get('commentid')
		self.postid = data.get('postid')
		self.text = data.get('text')
		self.date = data.get('date')
		self.commenter = data.get('commenter')
		return self