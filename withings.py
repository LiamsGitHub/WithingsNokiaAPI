# Class to get Withings OAuth1.0 keys and pull API data for activity, weight and sleep
# Liam Goudge March 2017. Refreshed March 2018.
# This is really useful site to test drive Withings APIs: https://developer.health.nokia.com/api#first_steps

import urllib 		# url-encode
import time 		# Unix timestamp
import datetime		# UNIX time for queries needing UNIX time
import hmac 		# Signing
import hashlib 		# Signing
import random 		# once generation
import base64 		# Conversion of hmac hash from bytes to human-readable string
import json			# Obvious...


class WithingsClient():
	
	params = {}
	
	def __init__ (self, userid = "", oauth_token = "", access_token_secret = "", oauth_callback = "", oauth_consumer_key = "", oauth_consumer_secret = ""):
	
		self.params["oauth_callback"] = self.url_encode(oauth_callback) 	# Have to pre-encode URL so URL ends up encoded twice. Not sure this is a spec requirement or Withings bug.
		self.params["oauth_consumer_key"] = oauth_consumer_key
		self.params["oauth_consumer_secret"] = oauth_consumer_secret		
		self.params["oauth_signature_method"] = "HMAC-SHA1"
		self.params["oauth_version"] = "1.0"
		self.params["userid"] = userid
		self.params["startdate"] = ""
		self.params["enddate"] = ""
		self.params["startdateymd"] = ""
		self.params["enddateymd"] = ""
		self.params["action"] = ""
		self.params["special_parameters"] = ""
		
		self.params["oauth_token"] = oauth_token					# Withings also calls this the access_token_key. Made in step 3
		self.params["oauth_token_secret"] = access_token_secret		# Made in step 3.

		self.basic_parameters = ["action","oauth_consumer_key","oauth_nonce","oauth_signature_method","oauth_timestamp","oauth_token","oauth_version","userid"]
		self.basic_token_parameters = ["oauth_callback","oauth_consumer_key","oauth_nonce","oauth_signature_method","oauth_timestamp","oauth_version"]
	
	
		# Get token if required
		if  not self.params["oauth_token"] or not self.params["oauth_token_secret"]:
			print ("Going through OAuth1.0 to request token and secret...")
			self.DoOAuth()
	
	# These functions perform the OAuth1.0 authorization steps

	def url_encode(self, data):
		return urllib.quote(data, "")

	def _get_nonce(self):
		# Random number to ensure each OAuth call is unique and prevent record attacks
		r = random.randint(1, 999999999)
		return r

	def _get_timestamp(self):
		return int(time.time())
			
	def make_dates(self,start_date,end_date):
	
		self.params["startdateymd"] = start_date
		self.params["enddateymd"] = end_date

		yy_start = start_date[0:4]
		mm_start = start_date[5:7]
		dd_start = start_date[8:]
		yy_end = end_date[0:4]
		mm_end = end_date[5:7]
		dd_end = end_date[8:]
		
		try:
			self.params["startdate"] = str(datetime.datetime(int(yy_start),int(mm_start),int(dd_start),12,0).strftime("%s"))
			self.params["enddate"] = str(datetime.datetime(int(yy_end),int(mm_end),int(dd_end),12,0).strftime("%s"))
			
		except:
			print ("Bad date error")
			exit()

		return

	def make_sig_and_url(self,endpoint,type,hash1,hash2): # Parameters are: endpoint and the 2 secrets for the hash function

		base_string = ""
		req_url = endpoint
	
		self.params["oauth_nonce"] = str(self._get_nonce())
		self.params["oauth_timestamp"] = str(self._get_timestamp())
	
		if (type == "data"):
			parameters = self.basic_parameters + self.params["special_parameters"]
		
		else:
			parameters = self.basic_token_parameters + self.params["special_parameters"]
	
		parameters.sort()

		for key in parameters:
			base_string = base_string + key + "=" + self.params[key] + "&"

		base_string = base_string[:len(base_string)-1] # remove trailing &
		base_string = "GET&" + self.url_encode(endpoint) + "&" + self.url_encode(base_string)
		# 2 significant bugs here. (1) Withings puts a "&" between getmeas and action (should be a ? since action is a parameter of getmeas (2) Withings does not URL_encode the & but leaves it as &
	
		base_decode = urllib.unquote(base_string).decode("utf8") 

		print ("Request base secret and URL:")
		print (base_string)
		#print (base_decode)
	
		hmacAlg = hmac.HMAC(hash1 + "&" + hash2, base_string, hashlib.sha1).digest() # as of step 2 there is a BUG and no %& is appended to the secret. Works in step2,3 and 4

		# base64 encode
		b64 = base64.b64encode(hmacAlg)
	
		# url encode
		self.params["oauth_signature"] = self.url_encode(b64)
	
		parameters = parameters + ["oauth_signature"]
		req_url = req_url + "?"
	
		for key in parameters:
			req_url = req_url + key + "=" + self.params[key] + "&"
	
		req_url = req_url[:len(req_url)-1] # remove trailing &
		print (req_url)
	
		return (req_url)
		
	def do_the_read(self,theurl):
		
		try:
			handle = urllib.urlopen(theurl)
			return(handle.read())
			
		except:
			print ("URL access error. Exiting")
			exit()
			
	def check_for_errors(self, status):
	
		error_dict = {
			0 : "Operation was successful",
			247 : "The userid provided is absent, or incorrect",
			250 : "The provided userid and/or Oauth credentials do not match",
			283 : "Token is invalid or doesn't exist",
			286 : "No such subscription was found",
			293 : "The callback URL is either absent or incorrect",
			294 : "No such subscription could be deleted",
			304 : "The comment is either absent or incorrect",
			305 : "Too many notifications are already set",
			328: "The user is deactivated",
			342 : "The signature (using Oauth) is invalid",
			343 : "Wrong Notification Callback Url don't exist",
			601 : "Too Many Request",
			2554 : "Wrong action or wrong webservice",
			2555 : "An unknown error occurred",
			2556 : "Service is not defined",
			401 :	"Unknown token error" }
			
		try:
			return (status, error_dict[status])
			
		except:
			return (status, "Reply status: unknown error")
		
		return
		
	
	def request_token(self):

		print ("Requesting temporary token and secret...")

		self.endpoint = "https://developer.health.nokia.com/account/request_token"
		self.params["special_parameters"]=[]
		theurl = self.make_sig_and_url(self.endpoint,"token",self.params["oauth_consumer_secret"],"")
	
		data = self.do_the_read(theurl)
	
		splitter = data.split("&")
		token = splitter[0].split("=")
		secret = splitter[1].split("=")
		self.params["oauth_token"] = str(token[1])
		self.params["oauth_token_secret"] = str(secret[1])
	
		print ("Temporary key and secret are:")
		print (self.params["oauth_token"],self.params["oauth_token_secret"])

		return
	
	
	def get_user_auth(self):

		print ("Getting User authorization...")

		endpoint = "https://developer.health.nokia.com/account/authorize"
		self.params["special_parameters"]=["oauth_token"]
		theurl = self.make_sig_and_url(endpoint,"token",self.params["oauth_consumer_secret"],self.params["oauth_token_secret"])

		print ("\nPlease paste the following URL into your favorite browser and then grant access to your Withings account")
		print ("")
		print (theurl)
	
		return


	def get_access_token(self):

		print ("Getting final access token and secret...")

		endpoint = "https://developer.health.nokia.com/account/access_token"
		self.params["special_parameters"]=["oauth_token"]
		theurl = self.make_sig_and_url(endpoint,"token",self.params["oauth_consumer_secret"],self.params["oauth_token_secret"])

		data = self.do_the_read(theurl)
	
		splitter = data.split("&")
		token = splitter[0].split("=")
		secret = splitter[1].split("=")
		self.params["oauth_token"] = token[1]
		self.params["oauth_token_secret"] = secret[1]
	
		print ("Final key and secret are:")
		print (self.params["oauth_token"],self.params["oauth_token_secret"])

		return
		
	def DoOAuth(self):
		self.request_token()
		self.get_user_auth()
		
		self.params["userid"] = raw_input("Enter the userid from the callback URL: ")
		self.get_access_token()
		
		return

	



	# These methods actually get the user data
	# Get body measures (weight etc) listing for given date range in UNIX format
	# Returns tuple of query status and a list of measurement objects
	def body_measures(self):
		endpoint = "http://api.health.nokia.com/measure"
		self.params["action"] = "getmeas"
		self.params["special_parameters"] = ["startdate","enddate"]
		
		output_data = []
		measurement = []
		
		measures = {1: ("Weight","kg"), 
			4: ("Height","m"), 
			5: ("Fat free mass","kg"), 
			6: ("Fat ratio","%"), 
			8: ("Fat mass weight","kg"), 
			9: ("Diastolic Blood Pressure","mmHg"), 
			10: ("Systolic Blood Pressure","mmHg"),
			11: ("Heart rate","bpm"),
			12: ("Temperature","DegC"),
			54: ("SP02","%"),
			71: ("Body Temperature","DegC"),
			73: ("Skin Temperature","DegC"),
			76: ("Muscle Mass","kg"),
			77: ("Hydration","%"),
			88: ("Bone Mass","kg"),
			91: ("Pulse Wave Velocity","m/s") }
	
		theurl = self.make_sig_and_url(endpoint,"data",self.params["oauth_consumer_secret"],self.params["oauth_token_secret"])
		data = self.do_the_read(theurl)

		json_data = json.loads(data)
		
		err_num,err_desc = self.check_for_errors(json_data["status"])

		if (err_num == 0):
		
			for group in json_data["body"]["measuregrps"]:
				date = str(datetime.datetime.fromtimestamp(group["date"]))

				for entry in group["measures"]:
					unit = measures[entry["type"]]
					value = entry["value"] * (10 ** entry["unit"])
					measurement = [date, unit[0], value, unit[1]]
					output_data.append(measurement)

			return (err_desc,output_data)
			
		else:
			return (err_desc,"")
	
	
	#Get activity listing for date range in format yyy-mm-dd
	# Returns tuple of query status and a list of activity objects
	def activity(self):
		endpoint = "https://api.health.nokia.com/v2/measure"
		self.params["action"] = "getactivity"
		self.params["special_parameters"] = ["startdateymd","enddateymd"]
		
		output_data = []
		measurement = []
	
		theurl = self.make_sig_and_url(endpoint,"data",self.params["oauth_consumer_secret"],self.params["oauth_token_secret"])
	
		data = self.do_the_read(theurl)
		print ("\nActivity data: ")

		json_data = json.loads(data)
		
		err_num,err_desc = self.check_for_errors(json_data["status"])
	
		if (err_num == 0):
		
			for group in json_data["body"]["activities"]:				
				measurement = [group["date"], group["steps"]]
				output_data.append(measurement)

			return (err_desc,output_data)
			
		else:
			return (err_desc,"")

	
	
	#Get sleep listing for date range in format yyy-mm-dd (API documentation is wrong: format is not UNIX)
	#Returns a tuple of query status and a list of sleep entry dictionaries
	def sleep(self):
		endpoint = "https://api.health.nokia.com/v2/sleep"
		self.params["action"] = "getsummary"
		self.params["special_parameters"] = ["startdateymd","enddateymd"]
		
		output_data = []
		measurement = []
	
		theurl = self.make_sig_and_url(endpoint,"data",self.params["oauth_consumer_secret"],self.params["oauth_token_secret"])
	
		data = self.do_the_read(theurl)
		print ("\nSleep data: ")

		json_data = json.loads(data)
		
		err_num,err_desc = self.check_for_errors(json_data["status"])
	
		if (err_num == 0):
		
			for group in json_data["body"]["series"]:
									
				measurement = [group["date"], group["data"]]
				output_data.append(measurement)

			return (err_desc,output_data)
			
		else:
			return (err_desc,"")
		

		return
	

	# Get workout listing for date range in yyyy-mm-dd format
	# Error in Withings documentation: API is called workouts not workout
	# Returns a tuple of query status and a list of workout entry dictionaries
	def workout(self):
		endpoint = "https://api.health.nokia.com/v2/measure"
		self.params["action"] = "getworkouts"
		self.params["special_parameters"] = ["startdateymd","enddateymd"]
		
		output_data = []
		measurement = []
		
		activity_type = {1 : "Walk",
						2 : "Run"}
	
		theurl = self.make_sig_and_url(endpoint,"data",self.params["oauth_consumer_secret"],self.params["oauth_token_secret"])
	
		data = self.do_the_read(theurl)
		print ("\nWorkout data: ")

		json_data = json.loads(data)
		
		err_num,err_desc = self.check_for_errors(json_data["status"])
		
		if (err_num == 0):
		
			for group in json_data["body"]["series"]:
			
				if (activity_type[group["category"]]):
					activity = activity_type[group["category"]]
				else:
					activity = "Other"
					
				measurement = [group["date"], activity, group["data"]]
				output_data.append(measurement)

			return (err_desc,output_data)
			
		else:
			return (err_desc,"")
		

		return


	



