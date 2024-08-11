
from flask import request, jsonify,current_app,g,make_response
from functools import wraps
from pymongo import MongoClient
from firebase_admin import app_check,credentials,auth

import flask
import jwt
import firebase_admin
import datetime


import os
# os.environ['GOOGLE_APPLICATION_CREDENTIALS'] =current_app.config['PATH']

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.join(os.getcwd(),'sv.json')
# Initialize Firebase Admin SDK
cred = credentials.Certificate(os.environ['GOOGLE_APPLICATION_CREDENTIALS'])
# print(cred)
firebase_admin.initialize_app(cred)
# print("done")
def get_db():
    if 'db' not in g:
        client = MongoClient(current_app.config['MONGO_URI'])
        g.db = client[current_app.config['DATABASE_NAME']]
    return g.db
def verify_token(f):
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        access_token = request.cookies.get('token')
        print(access_token)
        if access_token:
            try:
                email = None
                # Verify the JWT token using Firebase Auth
                decoded_token = auth.verify_id_token(access_token)

                if decoded_token['email_verified'] == False:
                    return jsonify({"error": "Email not verified"}), 400
                
                print(decoded_token)  # Optionally print the decoded token
                if not decoded_token:
                    return jsonify({"error": "Please login again."}), 400
                else:
                    email=decoded_token['firebase']['identities']['email'][0]
                    exp=decoded_token['exp']
                    # print(exp)
                    current_time = datetime.datetime.now().timestamp()
                    # print(current_time)
                    # print(exp>=current_time)
                #case 1: token is valid and expired 
                 #-check for refresh token i.e match from db and then generate a new access token and if want a refresh token too and then let them access the protected end point
                    if exp<current_time:
                        # print("expired")
                        try:
                            refresh_token=request.cookies.get('refreshtoken')
                            # print(refresh_token)
                            email=decoded_token['firebase']['identities']['email'][0]
                            # print(email)
                            db=get_db()
                            user=db['Accounts'].find_one({'email':email})
                            user_refresh_token=user['refreshtoken']
                            if refresh_token==user_refresh_token:
                                # print("refresh token matched")
                                refresh_expiry=user['refreshtokenexpiry']
                                current_time = datetime.datetime.now().timestamp()
                                if float(refresh_expiry.timestamp())>current_time:
                                    print("refresh token not expired")
                                    new_access_token=auth.create_custom_token(email).decode('utf-8')
                                    print("new accesstoken is",new_access_token)
                                    res = make_response(jsonify({"status": "Successfully logged in"}),200)
                                    res.set_cookie("token", new_access_token, httponly=True, samesite="None", secure=True)
                                    return res
                                else:
                                    return jsonify({"error": "Please login again"}), 400
                                
                            
                        except Exception as e:
                            print(e)
                
                
                
                return f(email,*args, **kwargs)
            except Exception as e:
                print(e)
                return jsonify({"error": "Unauthorized access"}), 400
        else:
            return jsonify({"error": "Unauthorized"}), 400
    return decorated_function
                
      
      
        
        
    
        

    