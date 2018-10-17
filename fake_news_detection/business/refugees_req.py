from fake_news_detection.dao.ElasticDao import Search
from fake_news_detection.utils.logger import getLogger



class callElDao():
	
	def __init__(self):
		self.search_callvar = Search()
	
	def DownloadAllReq(self):
		"""
		Request all the records
		@return: result_vec:list 
		"""
		result_vec =self.search_callvar.DownloadAll()

			
		return result_vec
	

	
	
	
	def GetLastDate(self):
		"""
		return the last date in which documents have been taken 
		@param : data: string
		@return : 
		"""
		
		lastdate = self.search_callvar.GetLastDate()
		return lastdate
	
	def GetDocsLastData(self):
		
		docs = self.search_callvar.DownloadPartial()
		return docs
		
		
	
		
		
	
if __name__ == "__main__" :
	
	c = callElDao()
	
	pippo = getLogger(__name__)
	pippo.debug("msg")
	#print(c.DownloadAllReq())
	print(c.GetLastDate())
	print(c.GetDocsLastData())
	
	
	del c