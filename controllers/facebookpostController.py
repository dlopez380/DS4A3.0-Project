from models.facebookpostModel import Facebookpost

class FacebookpostController(object):
	def __init__(self):
		self.model = Facebookpost()

	def all(self, filter=False):
		response = self.model.all()
		return response;

	def getByPostid(self, postId=False):
		response = self.model.getByPostid(postId)
		return response;

	def save(self, data):
		self.model.patch(data)
		response = self.model.save()
		return response;

	def update(self, data):
		# self.model.patch(data)
		response = self.model.update(data)
		return response;
