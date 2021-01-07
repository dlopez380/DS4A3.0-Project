from controllers.facebookpostController import FacebookpostController
from controllers.facebookcommentController import FacebookcommentController
from scrapper.selenium import extract
import json
import datetime

if __name__ == "__main__":

	begin_time = datetime.datetime.now()
	postsToFetch = 800
	# page = "https://www.facebook.com/offcorss"
	page = "https://www.facebook.com/Babyfreshoficial"
	# page = "https://www.facebook.com/epk/"
	posts = extract(page, postsToFetch, False, True)
	fp = 0
	fc = 0
	for post in posts:
		fp += 1
		# print(json.dumps(post, ensure_ascii=False, indent=2))
		post['facebookpage']=page
		exist = FacebookpostController().getByPostid(post['postid'])
		savedPostId = ""
		if exist:
			post['id'] = exist.id
			savedPostId = FacebookpostController().update(post)
		else:
			savedPost = FacebookpostController().save(post)
			savedPostId = savedPost.id
		for comment in post['featuredComments']:
			fc += 1
			cexist = FacebookcommentController().getByCommentId(post['featuredComments'][comment]['commentid'])
			post['featuredComments'][comment]['postid'] = savedPostId
			if cexist:
				post['featuredComments'][comment]['id'] = cexist.id
				savedComment = FacebookcommentController().update(post['featuredComments'][comment])
			else:
				savedComment = FacebookcommentController().save(post['featuredComments'][comment])
	print("Total posts fetched   : "+str(fp))
	print("Total comments fetched: "+str(fc))
	print("Execution time for "+str(postsToFetch)+" posts aprox: ")
	print(datetime.datetime.now() - begin_time)