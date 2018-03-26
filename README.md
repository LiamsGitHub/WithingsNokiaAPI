# WithingsNokiaAPI
Class to access health data collected by Withings Nokia devices

Withings Nokia have a set of connected health devices which allow you to track your activity, blood pressure, weight, fat mass, temperature, sleep etc.

The dataset is available via a set of APIs. Authorization is via OAuth1.0
I put together a Python class library for the authorization steps and data access for use as a module in an Alexa project on Lambda.

Usage:

`client = WithingsClient(userid, oauth_token, access_token_secret, oauth_callback, oauth_consumer_key, oauth_consumer_secret)`

Pass parameters are all string values where:

- userid: Withings-issued user ID for the customer. If none yet, pass “”
- oauth_token: Token issued from prior authorization for this customer. If none, pass “”.
- access_secret: Secret issued as above. If none, pass “” as above
- oauth_callback: In format http://www.site.com. OAuth process will call this after customer authorizes access.
- oauth_consumer_key: Developer key supplied on app registration at
- oauth_consumer_secret: Developer secret as above


If you pass “” for any of the token or secret values, this will trigger the OAuth authorization process.
Once a class instance is obtained, usage is as follows:
```
client.make_dates(“2017-03-01″,”2017-03-23”) # Sets query range. Format is yyyy-mm-dd. Start Date, End Date.
status,data = client.body_measures() # Get weighing scale data (weight, fat mass etc) and blood pressure
status,data = client.activity() # Get activity tracker data (steps etc)
status,data = client.sleep() # Get sleep data from either wrist tracker or Aura sleep pad
status, data = client.workout() # Get workout classification data'
```

Each of these return the data as a list of tuples or dictionaries like this:
```
Activity data:
Operation was successful
[u’2017-03-17′, 6410]
[u’2017-03-18′, 6909]

Sleep data:
Operation was successful
[u’2017-03-18′, {u’wakeupduration’: 600, u’deepsleepduration’: 7920, u’lightsleepduration’: 15720, u’durationtosleep’: 360, u’wakeupcount’: 1}]
[u’2017-03-19′, {u’wakeupduration’: 480, u’deepsleepduration’: 13500, u’lightsleepduration’: 20820, u’durationtosleep’: 180, u’wakeupcount’: 1}]

Workout data:
Operation was successful
[u’2017-03-17′, ‘Walk’, {u’metcumul’: 96.7411, u’distance’: 2291.37, u’hr_min’: 0, u’calories’: 83.57224, u’hr_average’: 0, u’intensity’: 9, u’steps’: 2597, u’hr_zone_3′: 0, u’hr_zone_2′: 0, u’effduration’: 1680, u’hr_zone_0′: 0, u’hr_zone_1′: 0, u’hr_max’: 0}]

Weight data:
Operation was successful
[‘2017-03-21 07:11:46’, ‘Heart rate’, 85, ‘bpm’]
[‘2017-03-21 07:11:46’, ‘Weight’, 81.013, ‘kg’]
[‘2017-03-21 07:11:46’, ‘Fat mass weight’, 15.444, ‘kg’]
```
Developer documentation is here.

To get a Developer Key, your “app” needs to be registered in a Withings Nokia Developer account available here.

The most useful page on the Developer site is the OAuth test mechanism which you can use step by step through the OAuth process to see how URLs, base signature and secret is built. Without this, I would likely not have got my code to work….
https://developer.health.nokia.com/api#step1

You may notice that I didn’t use the usual Python OAuth1.0 libraries. This was for 2 reasons:

(1) I believe the Withings implementation has 2 issues which mean the standard framework will not work without tweaking.

Issue#1: the URL for the OAuth base secret and the actual URL differ:
```
Base string: GET&http://api.health.nokia.com/measure&action=getmeas&oauth_consumer_key= ….etc
URL: http://api.health.nokia.com/measure?action=getmeas&oauth_consumer_key= …etc
```
Issue#2: the ‘&’ in call is not URL encoded like the rest of the base secret.

For example, this works:```
GET&http%3A%2F%2Fapi.health.nokia.com%2Fmeasure&action%3Dgetmeas%26oauth_consumer_key …etc
```
but this does not:```
GET&http%3A%2F%2Fapi.health.nokia.com%2Fmeasure%26action%3Dgetmeas&oauth_consumer_key ….etc
```
(2) Tinkering…

I just felt like tinkering with OAuth to see more closely how it worked. Using the class, you can get visibility of all stages of the OAuth process
