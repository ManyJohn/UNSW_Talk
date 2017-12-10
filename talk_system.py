import os,re,json
from pathlib import Path
import collections


class User_post(object):
	def __init__(self,comment,from_user,latitude,longitude,message,time,post_id):
		self.comment=comment#a list
		self.from_user=from_user
		self.latitude=latitude
		self.longitude=longitude
		self.lines=message#a list
		self.time=time
		self.post_id=post_id
	
	@classmethod
	def _remove_post(cls,students_dir,owner_zid,post_id,post_dict):
		full_filename = os.path.join(students_dir,owner_zid,post_id+'.txt')
		os.remove(full_filename)

	@classmethod
	def delete_post(cls,students_dir,owner_zid,post_id,word_ref,post_dict):
		if len(post_id.split("-"))==1:
			for comment_id in post_dict[owner_zid][post_id]['comments']:
				for reply_id in post_dict[owner_zid][comment_id]['comments']:
					cls._remove_post(students_dir,owner_zid,reply_id,post_dict)
					post_dict[owner_zid][comment_id]['comments'].remove(post_id)
				cls._remove_post(students_dir,owner_zid,comment_id,post_dict)
			post_dict[owner_zid]['all_post'].remove(post_id)
			cls._remove_post(students_dir,owner_zid,post_id,post_dict)
		elif len(post_id.split("-"))==2:
			''' it is a comment'''
			comment_id=post_id
			for reply_id in post_dict[owner_zid][comment_id]['comments']:
					cls._remove_post(students_dir,owner_zid,reply_id,post_dict)
					post_dict[owner_zid][comment_id]['comments'].remove(reply_id)
			cls._remove_post(students_dir,owner_zid,comment_id,post_dict)
			post_dict[owner_zid][comment_id.split('-')[0]]['comments'].remove(comment_id)
		elif len(post_id.split("-"))==3:
			'''it is a reply'''
			reply_id=post_id
			comment_id='-'.join(post_id.split("-")[0:2])
			cls._remove_post(students_dir,owner_zid,post_id,post_dict)
			post_dict[owner_zid][comment_id]['comments'].remove(reply_id)

	@classmethod
	def record_new_post(cls,students_dir,message,post_dict,user_from,word_ref):
		

		original_poster_zid=user_from
		if len(post_dict[original_poster_zid]['all_post'])!=0:
			original_file_name = str(int(post_dict[original_poster_zid]['all_post'][::-1][0])+1)
		else:
			#if the user have not made any post before
			original_file_name = '0'
		full_new_file_name=original_file_name+'.txt'

		
		for word in message.split():
			'''put_word_in_dict(all_word_dict,word,zid,post_num):'''
			Talk_system.put_word_in_dict(word_ref,word,user_from,original_file_name)
		with open('sys_word_ref','w') as f:
			f.write(json.dumps(word_ref))

		#write on a file
		full_filename = os.path.join(students_dir,original_poster_zid,full_new_file_name)
		if not os.path.isfile(full_filename) :
			with open(full_filename,'w') as f:
				f.write("message: "+message+'\n')
				f.write("from: "+user_from+'\n')
			post_dict[original_poster_zid][original_file_name]={}
			post_dict[original_poster_zid][original_file_name]['comments']=[]
			post_dict[original_poster_zid]['all_post'].append(original_file_name)

	@classmethod
	def record_new_comment(cls,students_dir,message,post_id_got,post_dict,user_from,word_ref):
		original_poster_zid=post_id_got[0:8]
		original_file_name=post_id_got[8:]
		
		'''constructs a new file name to record the comments''' 
		if len(post_dict[original_poster_zid][original_file_name]['comments'])!=0:
			#there already some comments for an original post

			new_file_name=original_file_name+'-'+str(int(post_dict[original_poster_zid][original_file_name]['comments'][::-1][0].split('-')[-1])+1)
			full_new_file_name=str(new_file_name)+'.txt'
		else:
			#the new post is the first comment for the original post
			new_file_name=str(original_file_name)+'-0'
			full_new_file_name=new_file_name+'.txt'

		for word in message.split():
			'''put_word_in_dict(all_word_dict,word,zid,post_num):'''
			Talk_system.put_word_in_dict(word_ref,word,user_from,original_file_name)
		with open('sys_word_ref','w') as f:
			f.write(json.dumps(word_ref))


		full_filename = os.path.join(students_dir,original_poster_zid,full_new_file_name)
		if not os.path.isfile(full_filename) :
			with open(full_filename,'w') as f:
				f.write("message: "+message+'\n')
				f.write("from: "+user_from+'\n')
			post_dict[original_poster_zid][new_file_name]={}
			post_dict[original_poster_zid][new_file_name]['comments']=[]
			post_dict[original_poster_zid][original_file_name]['comments'].append(new_file_name)




	@classmethod
	def load_post_without_comment(cls,post_dict,students_dir,zid,post_num,user_dict,root_url):
		details_filename = os.path.join(students_dir,zid,str(post_num)+'.txt')
		try:
			with open(details_filename) as f:
				detail_post_dict={line.split(': ')[0]:line.split(': ')[1][:-1] for line in f}
				for attribute in ['message','latitude','time','longitude','from']:
					if attribute not in detail_post_dict.keys():
						detail_post_dict[attribute]=None
				msg=detail_post_dict['message']
				if msg:
						replacer=re.compile('\s*(?P<name>z\d{7})\s*')
						for id_mentioned in replacer.findall(msg):
							if id_mentioned in user_dict.keys():
								msg=re.sub(id_mentioned,r'<a href="'+root_url+'visiting/'+id_mentioned+'"> '+user_dict[id_mentioned]['full_name']+'  </a>',msg,0)
						msg=msg.split('\\n')
				user_post=User_post(None,detail_post_dict['from'],\
					detail_post_dict['latitude'],detail_post_dict['longitude'],msg,detail_post_dict['time'],zid+post_num)
				return user_post
		except:
			return 


	@classmethod
	def load_post_by_detail(cls,post_dict,students_dir,zid,post_num,user_dict,root_url):
		details_filename = os.path.join(students_dir,zid,str(post_num)+'.txt')
		with open(details_filename) as f:
			detail_post_dict={line.split(': ')[0]:line.split(': ')[1][:-1] for line in f}
			for attribute in ['message','latitude','time','longitude','from']:
				if attribute not in detail_post_dict.keys():
					detail_post_dict[attribute]=None
			msg=detail_post_dict['message']
			#print("-------------msg is",msg)
			if msg:
				replacer=re.compile('\s*(?P<name>z\d{7})\s*')
				for id_mentioned in replacer.findall(msg):
					if id_mentioned in user_dict.keys():
						msg=re.sub(id_mentioned,r'<a href="'+root_url+'visiting/'+id_mentioned+'"> '+user_dict[id_mentioned]['full_name']+'  </a>',msg,0)
				msg=msg.split('\\n')

			if len(str(post_num).split('-')) == 3:
				''' it means that is post is a rply'''
				user_post=User_post(None,detail_post_dict['from'],\
				detail_post_dict['latitude'],detail_post_dict['longitude'],msg,detail_post_dict['time'],zid+post_num)
				return user_post

			user_post=User_post(post_dict[zid][str(post_num)]['comments'],detail_post_dict['from'],\
				detail_post_dict['latitude'],detail_post_dict['longitude'],msg,detail_post_dict['time'],zid+post_num)
			
			comment_list=[]
			for comt_num in post_dict[zid][str(post_num)]['comments'][::-1]:
				details_filename = os.path.join(students_dir,zid,str(comt_num)+'.txt')
				with open(details_filename) as f:
					detail_post_dict={line.split(': ')[0]:line.split(': ')[1][:-1] for line in f}
					for attribute in ['message','latitude','time','longitude','from']:
						if attribute not in detail_post_dict.keys():
							detail_post_dict[attribute]=None
					msg=detail_post_dict['message']
					#print("-------------msg is",msg)
					if msg:
						replacer=re.compile('\s*(?P<name>z\d{7})\s*')
						for id_mentioned in replacer.findall(msg):
							if id_mentioned in user_dict.keys():
								msg=re.sub(id_mentioned,r'<a href="'+root_url+'visiting/'+id_mentioned+'"> '+user_dict[id_mentioned]['full_name']+'  </a>',msg,0)
						msg=msg.split('\\n')

					if len(str(post_num).split('-')) == 2:
						''' it means that is post is a comment '''
						user_comment=User_post(None,detail_post_dict['from'],\
							detail_post_dict['latitude'],detail_post_dict['longitude'],\
							msg,detail_post_dict['time'],zid+comt_num)
					else:

						user_comment=User_post(post_dict[zid][str(comt_num)]['comments'],detail_post_dict['from'],\
							detail_post_dict['latitude'],detail_post_dict['longitude'],\
							msg,detail_post_dict['time'],zid+comt_num)
						
						reply_list=[]
						for reply_num in post_dict[zid][str(comt_num)]['comments'][::-1]:
							details_filename = os.path.join(students_dir,zid,str(reply_num)+'.txt')
							with open(details_filename) as f:
								detail_post_dict={line.split(': ')[0]:line.split(': ')[1][:-1] for line in f}
								for attribute in ['message','latitude','time','longitude','from']:
									if attribute not in detail_post_dict.keys():
										detail_post_dict[attribute]=None
								msg=detail_post_dict['message']
								#print("-------------msg is",msg)
								if msg:
									replacer=re.compile('\s*(?P<name>z\d{7})\s*')
									for id_mentioned in replacer.findall(msg):
										if id_mentioned in user_dict.keys():
											msg=re.sub(id_mentioned,r'<a href="'+root_url+'visiting/'+id_mentioned+'"> '+user_dict[id_mentioned]['full_name']+'  </a>',msg,0)
									msg=msg.split('\\n')
								user_reply=User_post(None,detail_post_dict['from'],\
									detail_post_dict['latitude'],detail_post_dict['longitude'],\
									msg,detail_post_dict['time'],zid+reply_num)
								reply_list.append(user_reply)

						user_comment.comment=reply_list
						comment_list.append(user_comment)
			user_post.comment=comment_list
			return user_post





class User(object):
	"""docstring for User"""
	def __init__(self, full_name,friends,birthday,home_longitude,email,\
		course_enroled,home_latitude,zid,program,home_suburb,password,students_dir):
		
		self.zid=zid #unique text
		self.email=email #text
		self.password=password #text
		self.full_name = full_name #text
		self.friends=friends #list
		self.birthday=birthday #year-m-d
		self.home_longitude=home_longitude #num
		self.course_enroled=course_enroled #list
		self.home_latitude=home_latitude #num
		self.program=program #list
		self.home_suburb=home_suburb #list
		if  os.path.isfile("./"+students_dir+"/"+zid+"/img.jpg"):
			self.img_path="/"+students_dir+"/"+zid
		else:
			self.img_path=""
			
	
	def delete_img(self,students_dir):
		if  os.path.isfile("./"+students_dir+"/"+self.zid+"/img.jpg"):
			os.remove("./"+students_dir+"/"+self.zid+"/img.jpg")




	@classmethod
	def create_user_by_dict(cls,user_dict,students_dir):

		friends=user_dict['friends'] if user_dict['friends'] != None else None
		courses=user_dict['courses'] if user_dict['courses'] != None else None

		user=User(user_dict['full_name'],friends,user_dict['birthday'],\
			user_dict['home_longitude'],user_dict['email'],courses,\
			user_dict['home_latitude'],user_dict['zid'],user_dict['program'],\
			user_dict['home_suburb'],user_dict['password'],students_dir)
		return user

	def suggest_friends(self,user_dict,students_dir):
		if os.path.exists('all_course_enrollment'):
			with open('all_course_enrollment','r') as f:
				course_enrollment_dict=json.loads(f.read())
				f.close()
		else:
			course_enrollment_dict=None

		suggest_fri_dict={}
		'''the suggession we made is based on number of firends in common'''
		for fid in self.friends:
			a_friend=User.create_user_by_dict(user_dict[fid],students_dir)
			for person_meet_zid in a_friend.friends:
				if person_meet_zid in self.friends or person_meet_zid==self.zid:
					'''ignore those who has already been your firends'''
					continue

				if person_meet_zid not in suggest_fri_dict.keys():
					suggest_fri_dict[person_meet_zid]=1
				else:
					suggest_fri_dict[person_meet_zid]+=1

		'''give weight to the students enroled in the same course'''
		for course_name in self.course_enroled:
			if course_enrollment_dict[course_name]:
				for person_meet_zid in course_enrollment_dict[course_name]:
					if person_meet_zid in self.friends or person_meet_zid==self.zid:
						'''ignore those who has already been your firends'''
						continue
					if person_meet_zid not in suggest_fri_dict.keys():
						suggest_fri_dict[person_meet_zid]=2
					else:
						suggest_fri_dict[person_meet_zid]+=2


		result=collections.OrderedDict(sorted(suggest_fri_dict.items(),key=lambda t:t[1]))
		return list(result)[::-1]




class Talk_system(object):
	def __init__(self):
		self.user_detail=['full_name','birthday','home_longitude','home_longitude',\
			'email','home_latitude','program','home_suburb','zid','password','courses','friends']
	
	def record_new_user(self,students_dir,sys_user_dict,sys_post_ref,zid,email,password):
		sys_user_dict[zid]={}
		sys_user_dict[zid]['zid']=zid
		sys_user_dict[zid]['email']=email
		sys_user_dict[zid]['password']=password
		sys_user_dict[zid]['friends']=[]
		for detail in self.user_detail:
			if detail not in sys_user_dict[zid].keys():
				sys_user_dict[zid][detail]=""

		Talk_system.save_as_file('sys_user_dict',sys_user_dict)

		os.makedirs(os.path.join(students_dir,zid))
		sys_post_ref[zid]={}
		sys_post_ref[zid]['all_post']=[]
		Talk_system.save_as_file('sys_post_ref',sys_post_ref)

		

	@classmethod
	def delete_user(cls,students_dir,zid,sys_user_dict,suspended_list):
		sys_user_dict.pop(zid)
		Talk_system.save_as_file('sys_user_dict',sys_user_dict)
		suspended_list.append(zid)
		for user in sys_user_dict.keys():
			if zid in sys_user_dict[user]['friends']:
				sys_user_dict[user]['friends'].remove(zid)
		files = sorted(os.listdir(os.path.join(students_dir,zid)))
		for file in files:
			os.remove(os.path.join(students_dir,zid,file))
		os.rmdir(os.path.join(students_dir,zid))


	@classmethod
	def save_as_file(cls,file_name,content):
		with open(file_name,'w') as f:
			f.write(json.dumps(content))
			f.close()

	@classmethod
	def changeFriendStatus(cls,my_zid,other_zid,user_dict):
		if other_zid in user_dict[my_zid]["friends"]:
			try:
				user_dict[my_zid]["friends"].remove(other_zid)
				status=1

			except:
				status=0
				#print("my zid",my_zid)
				#print(user_dict[my_zid]["friends"])
				#print("friends zid",other_zid)
				#print("type is",type(user_dict[other_zid]["friends"]))
				#print(user_dict[other_zid]["friends"])
				#print("change friend status fail")
		else:
			""" they are not friends """
			try:
				user_dict[my_zid]["friends"].append(other_zid)
				status=1

			except:
				status=0
				#print("they are not friends")
				#print("change friend status fail")
		"""if change status success return 1, otherwise 0"""
		if status == 1 :
			with open('sys_user_dict','w') as f:
					#print("writing ... the file ")
					f.write(json.dumps(user_dict))
					f.close()

		return status



	@classmethod
	def checkFriends(cls,my_zid,other_zid,user_dict):
		status = 0 #assume their not friends 
		if other_zid in user_dict[my_zid]["friends"]:
			status = 1
		else:
			""" they are not friends """
		return status

	@classmethod
	def load_word_dict(cls,students_dir):
		all_word_dict={}
		students = sorted(os.listdir(students_dir))
		for student_to_show in students:
			if student_to_show[0] == '.':
				continue
			details_filename = os.path.join(students_dir, student_to_show)
			files=sorted(os.listdir(details_filename))
			#print("-------",student_to_show,"---------")
			for file in files:
				if file[0] == '.':
					continue
				if file[0].isdigit():
					'''it is a valid file name'''
					details_filename = os.path.join(students_dir, student_to_show, file)
					with open(details_filename) as f:
						for line in f:
							if line.split(': ')[0] == "message":
						
								new_line=line.replace(r'\n',' ')
								for word in new_line.split()[1:]:
									''' get rid of the "message: " '''
									Talk_system.put_word_in_dict(all_word_dict,word,student_to_show,file.split('.')[0])
								'''we are only intersted in the message line'''
								break
		#print(all_word_dict.keys())


		return all_word_dict
		
	@classmethod
	def put_word_in_dict(cls,all_word_dict,word,zid,post_num):
		word=re.sub("\W+",'',word,0)
		if word.lower() not in all_word_dict.keys():
			all_word_dict[word.lower()]={}
			all_word_dict[word.lower()][zid]=[] #zid number as key
			all_word_dict[word.lower()][zid].append(post_num) # eg. 0-0
		else:
			'''a word is already in the dict'''
			if zid not in all_word_dict[word.lower()].keys():
				all_word_dict[word.lower()][zid]=[] #zid number as key
				all_word_dict[word.lower()][zid].append(post_num) # eg. 0-0
			else:
				if post_num not in all_word_dict[word.lower()][zid]:
					all_word_dict[word.lower()][zid].append(post_num) 



	def load_users(self,students_dir):
		'''load all the user from the data set to the server'''
		all_course_enrollment={}
		all_user_dict={}
		students = sorted(os.listdir(students_dir))
		for student_to_show in students:
			if student_to_show[0] == '.':
				continue
			details_filename = os.path.join(students_dir, student_to_show, "student.txt")
			user_dict={}
			with open(details_filename) as f:
				user_dict={line.split(': ')[0]:line.split(': ')[1][:-1] for line in f}
				for detail in self.user_detail:
					if detail not in user_dict.keys():
						"""SET THE VALUE TO DEFAULT IF USER DID NOT ENTER SUCH DETAIL"""
						user_dict[detail]=None
				if user_dict["friends"] is not None:
					user_dict["friends"]=user_dict["friends"][1:-1].split(', ')
				if user_dict["courses"] is not None:
					user_dict["courses"]=user_dict["courses"][1:-1].split(', ')
					for course_name in user_dict["courses"]:
						if course_name not in all_course_enrollment.keys():
							all_course_enrollment[course_name]=[user_dict['zid']]
						else:
							all_course_enrollment[course_name].append(user_dict['zid'])
				#print(user_dict['zid'])
				all_user_dict[user_dict['zid']]=user_dict
		Talk_system.save_as_file('all_course_enrollment',all_course_enrollment)
		return all_user_dict

	def load_post_ref(self,students_dir):
		'''this funtion dones not provide the full content of a post'''
		all_post_dict={}

		students = sorted(os.listdir(students_dir))
		for student_to_show in students:
			if student_to_show[0] == '.':
				continue
			files=sorted(os.listdir(students_dir+'/'+student_to_show))
			#print("-------",student_to_show,"---------")
			all_the_post=[]
			all_post_dict[student_to_show]={}
			for file in files:
				if file[0] == '.':
					continue
				file=file.split('.')[0]
				if file[0].isdigit():
					file_name_parts=file.split('-')
					if len(file_name_parts)==1:
						#load the main post
						#print(file)
						comment_list=[]
						comment_reply_list=[]
						all_post_dict[student_to_show][file_name_parts[0]]={}
						for comment in files:
							comment=comment.split('.')[0]
							if len(comment.split('-'))==2 and file==comment.split('-')[0] :
								#load the comment for the main post
								#print (comment)	
								reply_list=[]

								for reply in files:
									reply=reply.split('.')[0]
									if len(reply.split('-'))==3 and comment.split('-')[0]==reply.split('-')[0] and comment.split('-')[1]==reply.split('-')[1]:
										#load the reply fo the comments
										#print(reply)
										reply_list.append(reply.split('-')[2])
										reply_list=sorted(reply_list,key=int)
								reply_list=[file_name_parts[0]+'-'+comment.split('-')[1]+'-'+name for name in reply_list[:]]
								#print(reply_list[:])
								comment_list.append(comment.split('-')[1])
								all_post_dict[student_to_show][file_name_parts[0]+'-'+comment.split('-')[1]]={}
								all_post_dict[student_to_show][file_name_parts[0]+'-'+comment.split('-')[1]]['comments']=reply_list
						comment_list=sorted(comment_list,key=int)
						comment_list=[file_name_parts[0]+'-'+name for name in comment_list]
						all_the_post.append(file_name_parts[0])
						all_post_dict[student_to_show][file_name_parts[0]]['comments']=comment_list
						#print(comment_list)
			#print(all_the_post)
			all_post_dict[student_to_show]['all_post']=sorted(all_the_post,key=int)

		return all_post_dict


