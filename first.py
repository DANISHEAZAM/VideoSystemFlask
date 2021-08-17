from flask import Flask, flash,request,session,render_template,redirect,url_for
from flask_restplus import Resource, Api
from flask_restplus import reqparse
import os
import json,psycopg2
import hashlib
import decimal
import random
import glob
from werkzeug.utils import secure_filename
app = Flask(__name__,static_folder='uploads')
app.secret_key = os.urandom(24)
api = Api(app)
# add your upload forlder path and db details
UPLOAD_FOLDER = '/home/bond/Desktop/python-Flask/tony_code/uploads'
conn=psycopg2.connect(host='localhost',user='postgres',dbname='postgres',password='1234')
#-----------
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER 
#add your size of video you want to allow to be uploaded
app.config['MAX_CONTENT_LENGTH'] = 64 * 1024 * 1024
@app.route('/home',methods=["GET","POST"])
def index():
    return render_template('login.html')
@app.route('/newuser',methods=["GET","POST"])
def newuser():
    return render_template('register.html')
@app.route('/logout',methods=["GET","POST"])
def logout():
    session['userid']=None
    session['username']=None
   
    return render_template('login.html')
@app.route('/adminsecretpage',methods=["GET","POST","PUT","DELETE"])
def adminsd():
    return render_template('adminpage.html')
@app.route('/adminsecretpage/posts/<key>',methods=["GET","POST","PUT","DELETE"])
def adminsp(key=None,comment=None):
    search=key
    
    if search=="" or search==None:
        return redirect(url_for('adminsd'))
    
    key="%"+search+"%"
    
    cursor=conn.cursor()
    try:
        cursor.execute("select video_id,video_name,video_path from video_data where video_name like %s",(key,));
        res=cursor.fetchall()
        video_id=[]
        video_name=[]
        video_path=[]
        for r in res:
            
            video_id.append(str(r[0]))
            video_name.append(str(r[1]))
            video_path.append(str(r[2]))
        
        return render_template('posts.html',ll=len(video_id),videoid=video_id,videoname=video_name,video_path=video_path)
    except Exception as e:
        return redirect(url_for('adminsd'))
    return redirect(url_for('adminsd'))
@app.route('/adminsecretpage/posts/',methods=["GET","POST","PUT","DELETE"])
def adminsd1():
    return render_template('adminpage.html')
@app.route('/adminsecretpage/comments//',methods=["GET","POST","PUT","DELETE"])
def adminsd2():
    return render_template('adminpage.html')
@app.route('/adminsecretpage',methods=["GET","POST","PUT","DELETE"])
def admins(key=None):
    search=key
    if search=="" or search==None:
        return redirect(url_for('adminsd'))
    print(search,flush=True)
    key="%"+search+"%"
    #conn=psycopg2.connect(host='localhost',user='postgres',dbname='postgres',password='1234')
    cursor=conn.cursor()
    try:
        cursor.execute("select video_id,video_name,video_path from video_data where video_name like %s;",(key,));
        res=cursor.fetchall()
        videoid=[]
        videoname=[]
        videopath=[]
        for r in res:
            videoid.append(str(r[0]))
            videoname.append(str(r[1]))
            videopath.append(str(r[2]))
        print(videopath,flush=True)
        return render_template('posts.html',ll=len(videoid),videoid=videoid,videoname=videoname,videopath=videopath)
    except Exception as e:
        return redirect(url_for('adminsd'))
    return redirect(url_for('adminsd'))


@app.route('/adminsecretpage/comments/<key>/<comment>',methods=["GET","POST","PUT","DELETE"])
def adminsc(key=None,comment=None):
    username=key
    comment=comment
    if username=="" or username==None or comment=="" or comment==None:
        return redirect(url_for('adminsd'))
    print(username,flush=True)
    print(comment,flush=True)
    key="%"+comment+"%"
    #conn=psycopg2.connect(host='localhost',user='postgres',dbname='postgres',password='1234')
    cursor=conn.cursor()
    try:
        cursor.execute("select comment_id,comment,username,video_id from comments where username =%s and comment like %s",(username,key));
        res=cursor.fetchall()
        cid=[]
        c=[]
        u=[]
        vid=[]
        for r in res:
            cid.append(str(r[0]))
            c.append(str(r[1]))
            u.append(str(r[2]))
            vid.append(str(r[3]))
        
        return render_template('comments.html',ll=len(cid),cid=cid,c=c,u=u,vid=vid)
    except Exception as e:
        return redirect(url_for('adminsd'))
    return redirect(url_for('adminsd'))





@app.route('/uploader', methods=["GET","POST"])
def upload_video():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    else:
        #conn=psycopg2.connect(host='localhost',user='postgres',dbname='postgres',password='1234')
        cursor=conn.cursor()
        
        
        filename = secure_filename(file.filename)
        cursor.execute("insert into video_data(author_name,author_userid,video_name,video_path,likes) values(%s,%s,%s,%s,%s);",(session['username'],session['userid'],filename,UPLOAD_FOLDER+filename,0));
        conn.commit()
        
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        flash('Video successfully uploaded and displayed below')
        return redirect("/play/"+str(filename)+"$id=<rr>")
    return redirect(request.url)
@app.route('/play/<filename>$id=<rr>', methods=["GET","POST"])
def play(filename=None,rr=None):
    if 'userid' not in session.keys():
        return redirect(url_for('index'))
    rr=''.join(random.choice('abcdEFGHijklMNOpq1234567890rst') for _ in range(10))

    file_list=glob.glob(UPLOAD_FOLDER+"/*.mp4")
    video_map={}
    for i in file_list:
        path=i
        name=i.replace(UPLOAD_FOLDER,'')
        video_map[path]=name
    
    print(filename,flush=True)
    if filename == None:
        flash('No image selected for playing')
        return redirect(request.url)
    else:
        #conn=psycopg2.connect(host='localhost',user='postgres',dbname='postgres',password='1234')
        cursor=conn.cursor()
        cursor.execute("select author_name,video_id from video_data where video_name=%s;",(filename,));
        res=cursor.fetchall()
        users=[]
        comments=[]
        res2=None
        if len(res)!=0:
            cursor.execute("select comment,username from comments where video_id=%s order by comment_id desc;",(str(res[0][1]),));
            res2=cursor.fetchall()
        if res2==None:
            comments=[]
            users=[]
        else:
            lll=0
            for r in res2:
                users.append(r[1])
                comments.append(r[0])
        flash('Video successfully uploaded and displayed below')
        cursor.execute("select video_name,video_path from video_data where gold=1;")
        res3=cursor.fetchall()
        gold={}
        print(res3,flush=True)
        if  len(res3)!=0:
            for k,v in video_map.items():
                #print("---"+v,flush=True)
                #print("--"+res3[0][1],flush=True)
                
                m="/"+str(res3[0][1]).replace(UPLOAD_FOLDER,"")
                #print("--"+m,flush=True)
                if str(v)==m:
                    print("=-----------",flush=True)
                    del video_map[k]
                    break
            
            gold[res3[0][1]]=res3[0][0]
        return render_template('play.html',gold=gold,rr=rr,users=users,l=len(comments),comments=comments,video_id=res[0][1],file_list=video_map, filename=filename,author=res[0][0])
    return redirect(request.url) 
#@app.route('/display/<filename>')
#def display_video(filename):
	
#	return redirect(url_for('static', filename='uploads/' + filename), code=301)
@app.route('/profile',methods=["GET","POST"])
def profile():
    rr=''.join(random.choice('abcdEFGHijklMNOpq1234567890rst') for _ in range(10))
    session['rr']=rr
    if 'userid' not in session.keys():
        return redirect(url_for('index'))
    file_list=glob.glob(UPLOAD_FOLDER+"/*.mp4")
    video_map={}
    for i in file_list:
        path=i
        name=i.replace(UPLOAD_FOLDER,'')
        video_map[path]=name
    print(file_list,flush=True)
    if session['userid']!=None:
        #conn=psycopg2.connect(host='localhost',user='postgres',dbname='postgres',password='1234')
        cursor=conn.cursor()
        cursor.execute("select * from user_data where userid=%s;",(session['userid'],))
        res=cursor.fetchall()
        data={}
        data['following']=decimal.Decimal(res[0][2])
        data['bio']=res[0][3]
        data['hobbies']=res[0][4]
        data['likes']=decimal.Decimal(res[0][5])
        data['interests']=res[0][6]
        cursor.execute("select video_name,video_path from video_data where gold=1;")
        res3=cursor.fetchall()
        print(res3,flush=True)
        gold={}
        if len(res3)!=0:
            for k,v in video_map.items():
                print("---"+v,flush=True)
                print("--"+res3[0][1],flush=True)
                m="/"+str(res3[0][1]).replace(UPLOAD_FOLDER,"")
                print("--"+m,flush=True)
                if str(v)==m:
                    print("=-----------",flush=True)
                    del video_map[k]
                    break
        
        if len(res3)==0 or res3==None:
            gold={}
        else:
            gold[res3[0][1]]=res3[0][0]
        return render_template('profilepage.html',gold=gold,rr=rr,file_list=video_map,userid=session['userid'],username=session['username'],data=data)
    return redirect(url_for('index'))

@api.route('/register',endpoint='register')
class UserRegistration(Resource):
    postparser = reqparse.RequestParser()
    postparser.add_argument('username',required=True, type=str,location='headers')
    postparser.add_argument('password',required=True, type=str,location='headers')
    postparser.add_argument('bio',required=True, type=str,location='headers')
    postparser.add_argument('payload',required=True,type=str,location='headers')

    @api.expect(postparser)
    def post(self):
        #conn=psycopg2.connect(host='localhost',user='postgres',dbname='postgres',password='1234')
        username=request.headers.get('username')
        password=request.headers.get('password')
        bio=request.headers.get('bio')
        myjson=json.loads(request.headers.get('payload'))
        print(myjson,flush=True)
        following=0
        likes=0
        ciphered_text = hashlib.md5(password.encode())
        cursor=conn.cursor()
        try:
            cursor.execute("Insert into user_data(username,password,following,bio,hobbies,likes,interests) values(%s,%s,%s,%s,%s,%s,%s)",(username,ciphered_text.hexdigest(),following,bio,json.dumps(myjson['hobbies']),likes,json.dumps(myjson['interests'])))
            conn.commit()
            
            return "User successfully registered",200
        except Exception as e:
            return "Something went wrong"+str(e),400
@api.route('/login',methods=["GET","POST"])
class login(Resource):
    postparser = reqparse.RequestParser()
    postparser.add_argument('username',required=True, type=str,location='headers')
    postparser.add_argument('password',required=True, type=str,location='headers')
    

    @api.expect(postparser)
    def post(self):
        session.pop('userid',None)
        username=request.headers.get('username')
        password=request.headers.get('password')
        print("trying for "+str(username),flush=True)
        #conn=psycopg2.connect(host='localhost',user='postgres',dbname='postgres',password='1234')

        ciphered_text = hashlib.md5(password.encode())
        cursor=conn.cursor()
        try:
            cursor.execute("select * from user_data where username=%s and password=%s;",(username,ciphered_text.hexdigest()))
            res=cursor.fetchall()
            
            print(res,flush=True)
            if len(res)!=0:
                
                session['username']=json.dumps(res[0][0])
                session['userid']=res[0][-1]
                
                print(session['username'],flush=True)
                result= "Logged in successfully for user "+str(res[0][0]+str(session['userid']))
            else:
                result="User name or password is wrong"
                
                return {"data":str(result)},400
            
            print(result,flush=True)
            print(ciphered_text.hexdigest(),flush=True)
            return "user successfully logged in",200
        except Exception as e:
            return "Something went wrong"+str(e),400
    
@api.route('/like',methods=["GET","POST"])
class like(Resource):
    postparser = reqparse.RequestParser()
    postparser.add_argument('filename',required=True, type=str,location='headers')
    postparser.add_argument('like',required=True, type=str,location='headers')
    postparser.add_argument('author',required=True, type=str,location='headers')
    @api.expect(postparser)
    def post(self):
        userid=request.headers.get('author')
        print("userid"+str(userid),flush=True)
        userid=str(userid)[5:-5]
        filename=request.headers.get('filename')
        like=request.headers.get('like')
        #conn=psycopg2.connect(host='localhost',user='postgres',dbname='postgres',password='1234')
        cursor=conn.cursor()
        try:
            cursor.execute("select likes from video_data where video_name=%s;",(filename,));
            res=cursor.fetchall()
            print(int(decimal.Decimal(res[0][0])),flush=True)
            if like=='like':
                
                l=int(decimal.Decimal(res[0][0]))+1
                print(l,flush=True)
                cursor.execute("update video_data set likes=%s where video_name=%s;",(l,str(filename)))
                conn.commit()
                cursor.execute("select likes from user_data where username=%s;",(userid,));
                res2=cursor.fetchall()
                ll=int(decimal.Decimal(res2[0][0]))+1
                if ll<0:
                    ll=0
                cursor.execute("update user_data set likes=%s where username=%s;",(ll,userid))
                conn.commit()
            else:
                l=int(decimal.Decimal(res[0][0]))-1
                print(l,flush=True)
                cursor.execute("update video_data set likes=%s where video_name=%s;",(l,str(filename)))
                conn.commit()
                cursor.execute("select likes from user_data where username=%s;",(userid,));
                res2=cursor.fetchall()
                ll=int(decimal.Decimal(res2[0][0]))-1
                if ll<0:
                    ll=0
                cursor.execute("update user_data set likes=%s where username=%s;",(ll,userid))
                conn.commit()
            return "success",200
        except Exception as e:
            return "Something went wrong"+str(e),400

@api.route('/follow',methods=["GET","POST"])
class follow(Resource):
    postparser = reqparse.RequestParser()
    postparser.add_argument('author',required=True, type=str,location='headers')
    postparser.add_argument('follow',required=True, type=str,location='headers')
    @api.expect(postparser)
    def post(self):
        
        userid=request.headers.get('author')
        print("userid"+str(userid),flush=True)
        userid=str(userid)[5:-5]
        print("userid"+str(userid),flush=True)
        follow=request.headers.get('follow')
        #conn=psycopg2.connect(host='localhost',user='postgres',dbname='postgres',password='1234')
        cursor=conn.cursor()
        try:
            
            cursor.execute("select following from user_data where username=%s;",(userid,));
            res=cursor.fetchall()
            print(int(decimal.Decimal(res[0][0])),flush=True)
            if follow=='follow author':
                l=int(decimal.Decimal(res[0][0]))+1
                if l<0:
                    l=0
                cursor.execute("update user_data set following=%s where username=%s;",(l,userid))
                conn.commit()
            else:
                
                l=int(decimal.Decimal(res[0][0]))-1
                if l<0:
                    l=0
                print(l,flush=True)
                cursor.execute("update user_data set following=%s where username=%s;",(l,userid))
                conn.commit()
            return "success",200
        except Exception as e:
            return "Something went wrong"+str(e),400
            
        
@api.route('/comment',methods=["GET","POST"])
class follow(Resource):
    postparser = reqparse.RequestParser()
    postparser.add_argument('author',required=True, type=str,location='headers')
    postparser.add_argument('comment',required=True, type=str,location='headers')
    postparser.add_argument('videoid',required=True, type=str,location='headers')
    @api.expect(postparser)
    def post(self):
        
        username=request.headers.get('author')
        print("userid"+str(username),flush=True)
        username=str(username)[5:-5]
        print("userid"+str(username),flush=True)
        comment=request.headers.get('comment')
        videoid=request.headers.get('videoid')
        #conn=psycopg2.connect(host='localhost',user='postgres',dbname='postgres',password='1234')
        cursor=conn.cursor()
        try:
            
            cursor.execute("insert into comments(comment,username,video_id) values(%s,%s,%s)",(comment,username,videoid));
            conn.commit()
            
            return "success",200
        except Exception as e:
            return "Something went wrong"+str(e),400
        
@api.route('/adminpost',methods=["GET","DELETE","PUT","POST"])
class adminpost(Resource):
    postparser = reqparse.RequestParser()
    postparser.add_argument('videoid',required=True, type=str,location='headers')
    @api.expect(postparser)
    def put(self):
        
        
        videoid=request.headers.get('videoid')
        #conn=psycopg2.connect(host='localhost',user='postgres',dbname='postgres',password='1234')
        cursor=conn.cursor()
        try:
            cursor.execute("update video_data set gold=0;");
            conn.commit()
            cursor.execute("update video_data set gold=1 where video_id=%s;",(videoid,));
            conn.commit()
            
            return "success",200
        except Exception as e:
            return "Something went wrong"+str(e),400
        
    deleteparser = reqparse.RequestParser()
    deleteparser.add_argument('videoid',required=True, type=str,location='headers')
    @api.expect(deleteparser)
    def delete(self):
        
        
        videoid=request.headers.get('videoid')
        #conn=psycopg2.connect(host='localhost',user='postgres',dbname='postgres',password='1234')
        cursor=conn.cursor()
        try:
            cursor.execute("select video_name from video_data where video_id=%s;",(videoid,));
            res=cursor.fetchall();
            os.remove(UPLOAD_FOLDER+"/"+str(res[0][0]))
            cursor.execute("delete from video_data where video_id=%s;",(videoid,));
            conn.commit()
            
            return "success",200
        except Exception as e:
            return "Something went wrong"+str(e),400

@api.route('/searchpost',methods=["GET","DELETE","PUT","POST"])
class searchpost(Resource):
    postparser = reqparse.RequestParser()
    postparser.add_argument('search',required=True, type=str,location='headers')
    @api.expect(postparser)
    def post(self):
        
        
        search=request.headers.get('search')
        key="%"+search+"%"
        #conn=psycopg2.connect(host='localhost',user='postgres',dbname='postgres',password='1234')
        cursor=conn.cursor()
        try:
            cursor.execute("select video_id,video_name,video_path from video_data where video_name like %s;",(key,));
            res=cursor.fetchall()
            
            return res,200
        except Exception as e:
            return "Something went wrong"+str(e),400
        
        
        
    deleteparser = reqparse.RequestParser()
    deleteparser.add_argument('cid',required=True, type=str,location='headers')
    
    @api.expect(deleteparser)
    def delete(self):
        
        
        cid=request.headers.get('cid')
        
        #conn=psycopg2.connect(host='localhost',user='postgres',dbname='postgres',password='1234')
        cursor=conn.cursor()
        try:
            
            cursor.execute("delete from comments where comment_id=%s;",(cid,));
            conn.commit()
            
            return "success",200
        except Exception as e:
            return "Something went wrong"+str(e),400
        
        
        
        

if __name__ == '__main__':
    app.run(debug=True)
    