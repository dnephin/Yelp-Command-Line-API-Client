import json
import oauth2
import optparse
import urllib
import urllib2


consumer_key = ''
consumer_secret = ''
auth_token = ''
token_secret = ''

search_format = 'http://api.yelp.com/v2/search?%s'
review_format = 'http://api.yelp.com/v2/business/%s'


def auth(url):

	# Sign the URL
	consumer = oauth2.Consumer(consumer_key, consumer_secret)
	oauth_request = oauth2.Request('GET', url, {})
	oauth_request.update({'oauth_nonce': oauth2.generate_nonce(),
                        'oauth_timestamp': oauth2.generate_timestamp(),
                        'oauth_token': auth_token,
                        'oauth_consumer_key': consumer_key})

	token = oauth2.Token(auth_token, token_secret)
	oauth_request.sign_request(oauth2.SignatureMethod_HMAC_SHA1(), consumer, token)
	signed_url = oauth_request.to_url()

	# Connect
	try:
		conn = urllib2.urlopen(signed_url, None)
		try:
			response = json.loads(conn.read())
		finally:
			conn.close()
	except urllib2.HTTPError, error:
		response = json.loads(error.read())

	return response


def search(term, location, offset=0, limit=20):
	url = search_format % urllib.urlencode({
		'term': term, 
		'location': location, 
		'offset': offset,
		'limit': limit
	})
	return auth(url)

def reviews(biz_id):
	url = review_format % biz_id
	return auth(url)
