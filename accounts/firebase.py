import pyrebase
import os

apikey="AIzaSyDjexzhrEuva2tEnatCjUdqXBv5EEEg-Jk"
authDomain="skillvault-15446.firebaseapp.com"

config = {
  "apiKey": apikey,
  "authDomain": authDomain,
  "databaseURL": None,
  "storageBucket":None

}
firebase = pyrebase.initialize_app(config)