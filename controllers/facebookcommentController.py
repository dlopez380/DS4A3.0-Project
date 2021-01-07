from models.facebookcommentModel import Facebookcomment

class FacebookcommentController(object):
	def __init__(self):
		self.model = Facebookcomment()

	def all(self, filter=False):
		response = self.model.all()
		return response;

	def getByCommentId(self, commentid=False):
		response = self.model.getByCommentId(commentid)
		return response;

	def save(self, data):
		self.model.patch(data)
		response = self.model.save()
		return response;

	def update(self, data):
		response = self.model.update(data)
		return response;
