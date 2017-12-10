import subprocess
class Email_sender(object):
	"""docstring for email_sender"""
	@classmethod
	def send(cls,email_address,message):
		try:
			subprocess.run("mutt -s UNSW Talk message  -- "+email_address+"|echo '"+message+"'",shell=True) 
		except:
			pass