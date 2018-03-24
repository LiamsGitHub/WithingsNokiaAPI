# Script to drive WithingsClient class for OAuth1.0 keys and activity, weight and sleep data
# If OAuth key/secret are not provided, WithingsClient class will go through OAuth1.0 process to get them
# Requires OAuth consumer key and secret (obtained by registering App on Withings Developer site)
# Liam Goudge March 2018.

from withings import WithingsClient

oauth_token = ""										# End user token here. Withings also calls this access_token_key. Can leave blank to trigger OAuth authorization.
access_token_secret = ""								# End user secret here. Can leave blank to trigger OAuth authorization.

oauth_callback = ""										# OAuth callback URL in the format http://www.anything.com
oauth_consumer_key = ""									# Developer key. This comes from app registration on the Withings Developer site. Cannot leave blank.
oauth_consumer_secret = ""								# Developer secret. Cannot leave blank.

userid = ""												# Comes from the URL when Withings triggers the OAuth callback


client = WithingsClient(userid, oauth_token, access_token_secret, oauth_callback, oauth_consumer_key, oauth_consumer_secret)

client.make_dates("2017-03-01","2017-03-23") 			# Call format is yyyy-mm-dd. Start Date, End Date.

print ("\nGetting weights \n")
status,data = client.body_measures()

print status
for item in data:
	print item

print ("\nGetting activity")
status,data = client.activity()
print status
for item in data:
	print item

print ("\nGetting sleep")
status,data = client.sleep()
print status
for item in data:
	print item


print ("\nGetting workouts")
status, data = client.workout()
print status
for item in data:
	print item