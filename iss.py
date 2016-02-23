import requests 
from redis import Redis
from rq_scheduler import Scheduler
from twilio.rest import TwilioRestClient

from datetime import datetime
import pytz

#open a connection to your redis server. 
redis_server = Redis()

#create a scheduler ojbect with your redis server. 
scheduler = Scheduler(connection=redis_server)

client = TwilioRestClient()


# method to request the next pass of the iss over a given lat and long
def get_next_pass(lat,lon):
	iss_url = 'http://api.open-notify.org/iss-pass.json'
	location = {'lat' : lat, 'lon': lon}
	response = requests.get(iss_url,params=location).json()
	
	# if case if we recieve a valid response
	if 'response' in response:
		next_pass = response['response'][0]['risetime']
		next_pass_datetime = datetime.fromtimestamp(next_pass, tz=pytz.utc)
		print('Next pass for {},{} is: {}'
			.format(lat,lon,next_pass_datetime))
		return next_pass_datetime

	# another if we don't recieve a valid response
	else:
		print('No ISS flyby can be determined for {},{}'.format(lat,lon))

def add_to_queue(phone_number, lat,lon):
	if not redis_server.exists(phone_number):
		client.messages.create(to=phone_number,from_='4242863171', body='Thanks for subscribing to ISS alears!')
	
	# add this phone number to Redis associate with "lat,lon"
	redis_server.set(phone_number, '{},{}'.format(lat,lon))


	#get the dateitime oject representing the next ISS flyby for this number. 
	next_pass_datetime = get_next_pass(lat,lon)

	if next_pass_datetime:
	#schedule a text to be sent at the time of the next flyby.
		scheduler.enqueue_at(nex_pass_datetime,notify_subscriber, phone_number)

		print('{} will be notified when ISS passes by {},{}'.format(phone_number,lat,lon))
	
	#export TWILIO_ACCOUNT_SID='ACe0499c23566aa56f040bd213a6a99cb9'
	#export TWILIO_AUTH_TOKEN='8c4450c6d6f210e016b153d2740cd5f8'


def notify_subscriber(phone_number):
	msg_body = "Look up1 you may not be able tto see if , but the ISS is passing above you right now!"
	lat,lon = redis_server.get(phone_number).split(',')
	client.messages.create(to=phone_number, from_='4242863171', body=msg_body)

	#add the subscriber to the queue to reviece their next flyby message.
	add_to_queue(phone_number,lat, lon)

	print('Message has been sent to {}'.format(phone_number))
	

		
