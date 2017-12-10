#!/usr/bin/python3

# written by z5119641 Qingchen Zhong October 2017
# as a starting point for COMP[29]041 assignment 2
# https://cgi.cse.unsw.edu.au/~cs2041/assignments/UNSWtalk/

import os,sys,json
from flask import Flask, render_template, session,redirect,url_for,request,send_from_directory
from talk_system import User,Talk_system,User_post
from send_email import Email_sender

if len(sys.argv) < 2: 
    students_dir = "dataset-medium";
else:
    students_dir = sys.argv[1]

app = Flask(__name__,static_url_path = "", static_folder = students_dir)
talk_system = Talk_system()


if not os.path.exists('sys_user_suspended_list'):
    sys_user_suspended_list =[]
    Talk_system.save_as_file('sys_user_suspended_list',sys_user_suspended_list)
else:
    with open('sys_user_suspended_list','r') as f:
       sys_user_suspended_list=json.loads(f.read())
       f.close()

if not os.path.exists('sys_description_dict'):
    sys_description_dict ={}
    Talk_system.save_as_file('sys_description_dict',sys_description_dict)
else:
    with open('sys_description_dict','r') as f:
       sys_description_dict=json.loads(f.read())
       f.close()

if not os.path.exists('sys_user_dict'):
    sys_user_dict = talk_system.load_users(students_dir)
    Talk_system.save_as_file('sys_user_dict',sys_user_dict)
else:
    with open('sys_user_dict','r') as f:
       sys_user_dict=json.loads(f.read())
       f.close()

sys_post_ref = talk_system.load_post_ref(students_dir)

'''keep a doc for sys_word_ref so that we don't need to wait to long'''
if not os.path.exists('sys_word_ref'):
    sys_word_ref = talk_system.load_word_dict(students_dir)
    Talk_system.save_as_file('sys_word_ref',sys_word_ref)
else:
    with open('sys_word_ref','r') as f:
       sys_word_ref=json.loads(f.read())
       f.close()



@app.route('/<path:path_name>/img.jpg',methods=['GET'])
def sent_img(path_name):
    print(path_name)
    return send_from_directory(path_name+'/','img.jpg')


@app.route('/logout',methods=['GET'])
def logout():
    session.pop('zid')
    return redirect(url_for("login"))


@app.route('/signin',methods=['GET','POST'])
def sign_in():
    status=""
    if request.method == "POST":
        zid=request.form.get('zid','')
        password=request.form.get('password','')
        email=request.form.get('email','')

        if zid and zid not in sys_user_dict.keys():
            talk_system.record_new_user(students_dir,sys_user_dict,sys_post_ref,zid,email,password)
            status="successfully sign in"
            #msg="you have sigin in to UNSW Talk, please check out this address"+str(url_for('start'))
            #Email_sender.send(email,msg)
            return redirect(url_for('login'))
        else:
            status="zid is invaild"
    return render_template('sign_in.html',status=status)

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == "POST":
        username=request.form.get('username','')
        password=request.form.get('password','')
        try:
            if sys_user_dict[username]['password'] == password:
                session['zid']=username
                return redirect(url_for("start"))
        except:
            session['zid']=''

    return render_template('login.html')


@app.route('/', methods=['GET','POST'])
#@app.route('/home', methods=['GET','POST'])
def start():
    if 'zid' not in session or session['zid']=="":
        return redirect(url_for("login"))
    #session['zid']="z5198757"
    if request.method=="POST":
        new_comment = request.form.get("editor","")
        id_commented_on = request.form.get("post_id","")
        delete=request.form.get("delete","")
        if delete:
            post_id=request.form.get("post_id","")
            #print("deleting",post_id)
            User_post.delete_post(students_dir,post_id[0:8],post_id[8:],sys_word_ref,sys_post_ref)
        else:
            if id_commented_on == "new_post":
                #user is making new post
                #print("new post is",new_comment)
                User_post.record_new_post(students_dir,new_comment,sys_post_ref,session['zid'],sys_word_ref)
            else:
                # user is commenting on a post
                #print("new comment is",new_comment)
                #print("the id being commented",id_commented_on)
                User_post.record_new_comment(students_dir,new_comment,id_commented_on,sys_post_ref,session['zid'],sys_word_ref)



    user=User.create_user_by_dict(sys_user_dict[session['zid']],students_dir)
    post_list=[User_post.load_post_by_detail(sys_post_ref,students_dir,session['zid'],post_id,sys_user_dict,url_for('start'))\
    for post_id in sys_post_ref[session['zid']]['all_post'][::-1]]

    if user.friends:
        friends=[User.create_user_by_dict(sys_user_dict[person_id],students_dir) for person_id in user.friends]
    else:
        friends=None
    if user.zid in sys_description_dict.keys():
        dscrp=sys_description_dict[user.zid]
    else:
        dscrp=""
    return render_template('home_page.html',me=user,user=user,friends=friends,post_list=post_list,description=dscrp)

@app.route('/search', methods=['GET','POST'])
def search():
    if 'zid' not in session or session['zid']=="":
        return redirect(url_for("login"))
    #session['zid']="z5190009"    
    me=User.create_user_by_dict(sys_user_dict[session['zid']],students_dir)
    if request.method == "POST":
        word_to_search = request.form.get('search','')
        frd_result=[]
        post_result=[]
        for zid in sys_user_dict.keys():
            if word_to_search.lower() in sys_user_dict[zid]['full_name'].lower():
                frd_result.append(User.create_user_by_dict(sys_user_dict[zid],students_dir))
        if word_to_search.lower() in sys_word_ref.keys():
             for zid in sys_word_ref[word_to_search.lower()].keys():
                for post_num in sys_word_ref[word_to_search.lower()][zid]:
                    post_Found=User_post.load_post_without_comment(sys_post_ref,students_dir,zid,post_num,sys_user_dict,url_for('start'))
                    if post_Found:
                        post_result.append(post_Found)
                    
        print(post_result)
                 #post_dict,students_dir,zid,post_num,user_dict
        return render_template("search_bar.html",result=frd_result,me=me,post_result=post_result)
    return render_template("search_bar.html",result=None,me=me)


@app.route('/visiting/<zid>', methods=['GET','POST'])
def visit(zid):
   
    if 'zid' not in session or session['zid']=="":
        return redirect(url_for("login"))

    me=User.create_user_by_dict(sys_user_dict[session['zid']],students_dir)
    if zid in sys_user_suspended_list:

        return render_template('suspend.html',me=me)

    if request.method=="POST":

        new_comment = request.form.get("editor","")
        id_commented_on = request.form.get("post_id","")
        change_fs=request.form.get("change_fs","")
        delete=request.form.get("delete","")
        
        if delete:
            post_id=request.form.get("post_id","")
            #print("deleting",post_id)
            User_post.delete_post(students_dir,post_id[0:8],post_id[8:],sys_word_ref,sys_post_ref)
        else:
            if id_commented_on:
                # user is commenting on a post
                #print("new comment is",new_comment)
                #print("the id being commented",id_commented_on)
                User_post.record_new_comment(students_dir,new_comment,id_commented_on,sys_post_ref,session['zid'],sys_word_ref)
            elif change_fs:
                Talk_system.changeFriendStatus(session['zid'],zid,sys_user_dict)

   
    user=User.create_user_by_dict(sys_user_dict[zid],students_dir)
    post_list=[User_post.load_post_by_detail(sys_post_ref,students_dir,zid,post_id,sys_user_dict,url_for('start'))\
    for post_id in sys_post_ref[zid]['all_post'][::-1]]

    if user.friends:
        friends=[User.create_user_by_dict(sys_user_dict[person_id],students_dir) for person_id in user.friends]
    else:
        friends=None
    
    ''' check if they are friends'''
    f_status=Talk_system.checkFriends(session['zid'],zid,sys_user_dict)
    if zid in sys_description_dict.keys():
        dscrp=sys_description_dict[zid]
    else:
        dscrp=""
    return render_template('visit_home.html',me=me,user=user,friends=friends,post_list=post_list,f_status=f_status,description=dscrp)



@app.route('/<zid>/friends', methods=['GET','POST'])
def view_friends(zid):
    if 'zid' not in session or session['zid']=="":
        return redirect(url_for("login"))
    me=User.create_user_by_dict(sys_user_dict[session['zid']],students_dir)
    user=User.create_user_by_dict(sys_user_dict[zid],students_dir)
    
    '''a list of zid will be return back'''
    f_suggeted = me.suggest_friends(sys_user_dict,students_dir)
    if len(f_suggeted)>10:
        f_suggeted=f_suggeted[:10]
        f_suggeted=[User.create_user_by_dict(sys_user_dict[person_id],students_dir) for person_id in f_suggeted ]
    elif len(f_suggeted)==0:
        f_suggeted=None
    else:
        f_suggeted=[User.create_user_by_dict(sys_user_dict[person_id],students_dir) for person_id in f_suggeted ]
    
    if user.friends:
        friends=[User.create_user_by_dict(sys_user_dict[person_id],students_dir) for person_id in user.friends]
    else:
        friends=None


    return render_template('friends.html',me=me,user=user,friends=friends,f_suggeted=f_suggeted)


@app.route('/setting',methods=['GET','POST'])
def setting():
    if 'zid' not in session or session['zid']=="":
        return redirect(url_for("login"))
    
    me=User.create_user_by_dict(sys_user_dict[session['zid']],students_dir)
    if me.zid in sys_description_dict.keys():
        dscrp=sys_description_dict[me.zid]
    else:
        dscrp=""

    if request.method=="POST":
        click_on=request.form.get("submit","")
        if click_on == "delete img":
            me.delete_img(students_dir)
        elif  click_on == "new img":
            file = request.files['new_img']
            if file.filename == '':
                return  render_template('setting.html',me=me,description="I'm geniues")
            elif file and file.filename.split('.')[1].lower()=="jpg":
                '''the user upload a real jpg'''
                '''store the img in user's folder'''
                filename="img.jpg"
                app.config['UPLOAD_FOLDER'] = "./"+students_dir+"/"+me.zid+"/"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
        elif  click_on == "update":
            '''change user detail'''
            dscrp=request.form.get("description","")
            dscrp.replace("<","&lt;")
            dscrp.replace(">","&gt;")
            dscrp.replace("%","&amp;")
            #print(dscrp)
            sys_description_dict[me.zid]=dscrp
            with open('sys_description_dict','w') as f:
                f.write(json.dumps(sys_description_dict))
                f.close()

            home_suburb=request.form.get("home_suburb","")
            home_longitude=request.form.get("home_longitude","")
            home_latitude=request.form.get("home_latitude","")
            password=request.form.get("password","")
            full_name=request.form.get("full_name","")
            birthday=request.form.get("birthday","")
            program=request.form.get("program","")

            sys_user_dict[me.zid]['home_suburb']=home_suburb
            sys_user_dict[me.zid]['home_longitude']=home_longitude
            sys_user_dict[me.zid]['home_latitude']=home_latitude
            sys_user_dict[me.zid]['password']=password
            sys_user_dict[me.zid]['full_name']=full_name
            sys_user_dict[me.zid]['birthday']=birthday
            sys_user_dict[me.zid]['program']=program
            Talk_system.save_as_file('sys_user_dict',sys_user_dict)
            me=User.create_user_by_dict(sys_user_dict[session['zid']],students_dir)



        elif  click_on == "suspend account":
            if me.zid not in sys_user_suspended_list:
                sys_user_suspended_list.append(me.zid)
                Talk_system.save_as_file('sys_user_suspended_list',sys_user_suspended_list)
        elif click_on == "delete account":
            Talk_system.delete_user(students_dir,me.zid,sys_user_dict,sys_user_suspended_list)
            return redirect(url_for('login'))







        return render_template('setting.html',me=me,description=dscrp)
    

    return render_template('setting.html',me=me,description=dscrp)




if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.run(debug=True)
    
    
