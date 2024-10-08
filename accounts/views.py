from flask import g,current_app,request,jsonify,make_response

import re
import os
from pymongo import MongoClient

from  .firebase import firebase
from PIL import Image
import datetime
from .middleware import verify_token  
import base64
from io import BytesIO
from flask import send_from_directory

import uuid
auth=firebase.auth()
def get_db():
    if 'db' not in g:
        client = MongoClient(current_app.config['MONGO_URI'])
        g.db = client[current_app.config['DATABASE_NAME']]
    return g.db

def register():
    db=get_db()
    try:
        if 'name' not in request.form.keys():
            return jsonify({"error":"Name is required"}),500
        else :
            name=request.form["name"]
            if not re.match("^[A-Za-zÀ-ÖØ-öø-ÿ' -]+$",name):
                return jsonify({"error":"Name is invalid"}),500
        if 'email' not in request.form.keys():
            return jsonify({"error":"Email is required"}),500
        else:
            email=request.form['email']
            if not re.match("^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$",email):
                return jsonify({"error":"Email is invalid"}),500
        if 'phone' not in request.form.keys():
            return jsonify({"error":"Phone Number is required"}),500
        else:
            phone=request.form['phone']
            if not re.match("^[0-9]{10}$",phone):
                return jsonify({"error":"Phone Number is invalid"}),500
        if 'college' not in request.form.keys():  
            return jsonify({"error":"College name is required.If you don't have one please type NA."}),500
        else:
            college=request.form['college']
        if 'university' not in request.form.keys():
            return jsonify({"error":"University name is required.If you don't have one please type NA."}),500
        else:
            university=request.form['university']

        if 'collegeidimage' not in request.files.keys():
            collegeidimage=None
            collegeid='Profile.jpg'
        else:
            collegeidimage=request.files['collegeidimage']
            if collegeidimage:
                ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
                file_name, ext =collegeidimage.filename.split('.')
                if ext not in ALLOWED_EXTENSIONS:
                    return jsonify({"error":"please provide a valid image file (jpg , jpeg and png allowed)"}),400
                file_name = f"{name}_collegeid_{uuid.uuid1()}.{ext}"
                if not os.path.exists(f"static/collegeids"):
                    os.mkdir(f"static/collegeids")
                collegeidimage = Image.open(collegeidimage)
                collegeidimage.thumbnail((600, 600))
                collegeidimage.save(f"static/collegeids/{file_name}")
                collegeid=file_name
            else:
                collegeid='Profile.jpg'
        
        
        
        if 'gender' in request.form.keys():
            gender=request.form['gender']
            gender=gender.lower()
        
        else:
            gender=None
       
        if 'pronouns' in request.form.keys(): 
            pronouns=request.form['pronouns']
            pronouns=pronouns.lower()
            
        else:
            pronouns=None
       
        if 'password' not in request.form.keys():
            return jsonify({"error":"Password is required"}),500
        else:
            password=request.form['password']
            if len(password)<6:
                return jsonify({"error":"Password must be atleast 6 characters long"}),500
            if not re.match("^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{6,}$",password):
                return jsonify({"error":"Password must contain atleast one uppercase,lowercase,number and special character"}),500
            try:
                try:
                    user=auth.create_user_with_email_and_password(email,password)
                    print("user created")
                    print(user)
                    auth.send_email_verification(user['idToken'])
                    print("email sent")
                except Exception as e:
                    return jsonify({"error":"Email already exists"}),500
                print("in mongo")
                db.Accounts.insert_one ({
                        'name':name,
                        'email':email,
                        'phone':phone,
                        'college':college,
                        'university':university,
                        'collegeid':collegeid,
                        'gender':gender,
                        'pronouns':pronouns,
                        'is_alloted':False, #offer letter sent -we ll let you know screen
                        'has_chosen': False,# chosen tech stack and all - select domain
                        'has_accepted':False,# offfer letter accepted - we ve sent offerleterr for acceptance 
                        
                    })
                print("inserted in mongo")
                
                #checking if acc created in mongo
                user=db.Accounts.find({'email':email})
                print(user)
                print("account created")
                return jsonify({"message":"Account created successfully"}),200
                
            except Exception as e:
                print(e)
                return jsonify({"error":"Error while creating account.Please try in sometime"}),500
            
    except Exception as e:
        return jsonify({"error":"Error while creating account.Please make sure you have provided every required field."}),500
        
    
    
  
def login():
    auth = firebase.auth()
    email=request.form['email']
    password=request.form['password']
    try:
        user=auth.sign_in_with_email_and_password(email,password)
        
        
        
        print(user)
        if user['registered']==False:
            return jsonify({"error":"Email not registered.Please Sign Up"}),400
        print("here")
        user_user=auth.get_account_info(user['idToken'])
        
        is_verified=user_user['users'][0]['emailVerified']
        if is_verified==False:
            return jsonify({"error":"Email not verified.Please verify your email"}),400
        token=user['idToken']
        refreshtoken=user['refreshToken']  
        db = get_db()
        expiry=datetime.datetime.now()+datetime.timedelta(days=7)
        db['Accounts'].update_one({'email':email},{'$set':{'refreshtoken':refreshtoken,'refreshtokenexpiry':expiry}})
        res = make_response(jsonify({"status": "Successfully logged in"}))
        res.set_cookie("token", token, httponly=True, samesite="None", secure=True, max_age=3600)
        print("set cookie")
        
        res.set_cookie("refreshtoken", refreshtoken, httponly=True, samesite="None", secure=True, max_age=60*60*24*5)
        
        return res
    except Exception as e:
        print(e)
        return jsonify({"error":"Invalid credentials"}),400
    
    """
    
    login regardless how many time- 1.login checks-emailexisitence
            -return everything new acces+refresh token-done   
            -database save refresh only with expiry 
            -save the access in http only  cookies by backend only and refresh also in cookies
    
    already logged in 
    -check if access token is valid
            -check the access toekn middleware ,if valid toh access kr skta hai
            -if not valid check the refresh token
                    -if refresh token is valid and not expired ,check from db ,then return new access token and refresh token
        
                    -if refresh token is expired or invalid ,login again return 400
                   
    
    """
@verify_token
def protected(user_mail):
    db = get_db()
    user=db.Accounts.find_one({'email':user_mail}, {'_id': False})
    print("this is user")

    return jsonify({"message":"you have got the access","user":user}),200


def logout():
    try:
        res = make_response(jsonify({"status": "Successfully logged out"}))
        res.set_cookie("token", '', expires=0, httponly=True, samesite="None", secure=True)
        res.set_cookie("refreshtoken", '', expires=0, httponly=True, samesite="None", secure=True)
        return res
    except Exception as e:
        return jsonify({"error":"Error while logging out"}),500
    



def resend_email_verification():
    
    try:
        email=request.form['email']
        user=auth.sign_in_with_email_and_password(email,request.form['password'])
        auth.send_email_verification(user['idToken'])
        return jsonify({"message":"Email verification sent"}),200
    except  Exception as e:
        return jsonify({"error":"Invalid credentials"}),400

def forgot_password():
    try:
        email=request.form['email']
        auth.send_password_reset_email(email)
        return jsonify({"message":"Password reset email sent.Please check your email"}),200
    except Exception as e:
        print(e)
        return jsonify({"message":"Password reset email sent.Please check your email"}),200


@verify_token
def profile(user_email):
    if request.method=='GET':
        try:
            db=get_db()
            email=user_email
            user=db.Accounts.find_one({'email':email})
            print(user)
            if user:
                return jsonify({"name":user['name'],"email":user['email'],"gender":user['gender'],"pronouns":user['pronouns'],"batch":user['batch'],"role":user['role'] , "profile": user['profilepicture']}),200

            else:
                return jsonify({"error":"No user found"}),400
        except Exception as e:
            print(e)
            return jsonify({"error":"Error while fetching profile"}),500
    if request.method=='PUT':
        try:
            db=get_db()
            email=user_email
            user=db.Accounts.find_one({'email':email})
            print(user)
            name = user['name']
            gender = user['gender']
            pronouns = user['pronouns']
            if 'name' in request.form.keys():
                    name=request.form['name']
                    if not re.match("^[A-Za-zÀ-ÖØ-öø-ÿ' -]+$",name):
                        return jsonify({"error":"Name is invalid"}),500
            if 'gender' in request.form.keys():
                    gender=request.form['gender']
                    
            if 'pronouns' in request.form.keys():
                    pronouns=request.form['pronouns']
            if 'profilepicture' in request.form and request.form['profilepicture'] != 'null':
                profilepicture = request.form['profilepicture']
                if profilepicture:
                    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

                if profilepicture.startswith('data:image/'):
                    header, profilepicture = profilepicture.split(',', 1)

                # Decode the Base64 string
                image_data = base64.b64decode(profilepicture)
                image = Image.open(BytesIO(image_data))

                # Generate a unique filename
                file_name = f"{name.split(" ")[0]}_profile_{uuid.uuid1()}.png"

                # Ensure the directory exists
                if not os.path.exists('static/profilepictures'):
                    os.makedirs('static/profilepictures')

                # Save the image
                image.thumbnail((600, 600))
                image.save(os.path.join('static/profilepictures', file_name))
                try:
                    old_profile = user['profilepicture']
                    os.remove(f"static/profilepictures/{old_profile}")
                except:
                    pass
            
                db.Accounts.update_one({'email':email},{'$set':{'name':name,'gender':gender,'pronouns':pronouns,'profilepicture':file_name}})

            
            else:
                db.Accounts.update_one({'email':email},{'$set':{'name':name,'gender':gender,'pronouns':pronouns}})

            return jsonify({"message":"Profile updated successfully"}),200
            
            
            
        except Exception as e:
            print(e)
            return jsonify({"error":"Error while updating profile"}),500
                    
@verify_token
def profile_picture(user_email,picture):
    print(picture)
    try:
        return send_from_directory('static/profilepictures', picture)
       
    except Exception as e:
        print(e)
        return jsonify({"error":"Error while fetching profile picture"}),500                 
        