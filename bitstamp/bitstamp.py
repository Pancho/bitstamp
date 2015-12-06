from configparser import ConfigParser
from datetime import datetime
import json
import hmac
import hashlib
import time


import websocket
import requests


EXAMPLES_URL = 'https://github.com/Pancho/bitstamp'
BITSTAMP_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
WS_CHANNEL_LIVE_TRADES = 'live-trades'
WS_CHANNEL_ORDER_BOOK = 'order-book'
WS_CHANNEL_ORDER_BOOK_DIFF = 'diff-order-book'
USER_TRANSACTION_ORDERING_DESC = 'desc'
USER_TRANSACTION_ORDERING_ASC = 'asc'


class Bitstamp(object):
	def __init__(self, config_file_path=None, api_key=None, secret=None, customer_id=None, api_endpoint=None):
		'''
		Constructor. You can instantiate this class with either file path or with all three values that would otherwise
		 be found in the config file.
		:param config_file_path: path to the file with the config
		:param api_key: API key found on https://www.bitstamp.net/account/security/api/
		:param secret: Secret found on https://www.bitstamp.net/account/security/api/ (disappears after some time)
		:param customer_id: Customer ID found on https://www.bitstamp.net/account/balance/
		:return: The client object
		'''
		# None of the parameters are necessary, but to work properly, we need at least one pair from one source
		if config_file_path is None and (api_key is None or secret is None or customer_id is None):
			raise Exception('You need to pass either config_file_path parameter or all of api_key, secret and customer_id')

		if config_file_path is not None:
			self.api_key, self.secret, self.customer_id = self.__get_credentials(config_file_path)
		else:
			self.api_key = api_key
			self.secret = secret
			self.customer_id = customer_id

		# If still not api key and no secret, raise
		if self.api_key is None or self.api_key.strip() == '' or self.secret is None or self.secret.strip() == '' or self.customer_id is None or self.customer_id.strip() == '':
			raise Exception('No credentials were found')

		if api_endpoint is None:
			self.api_endpoint = 'https://www.bitstamp.net/api/'
		else:
			self.api_endpoint = api_endpoint
		# Why didn't I use the pushed API?
		# 1. I wanted this client lib to be Python3 compatible - Pusher doesn't support that (clearly) yet
		# 2. Don't want all the ballast that comes along (a whole lib for three channels and supporting libs)
		self.websockets_endpoint = 'ws://ws.pusherapp.com/app/de504dc5763aeef9ff52?protocol=7'
		self.ws_channels = {  # Pusher wants JSON objects stringified (which is kind of weird, but due to it's generic nature it might make some sense)
			WS_CHANNEL_LIVE_TRADES: '{"event":"pusher:subscribe","data":{"channel":"live_trades"}}',
			WS_CHANNEL_ORDER_BOOK: '{"event":"pusher:subscribe","data":{"channel":"order_book"}}',
			WS_CHANNEL_ORDER_BOOK_DIFF: '{"event":"pusher:subscribe","data":{"channel":"diff_order_book"}}',
		}
		self.ws_data_events = ['data', 'trade']

	def __str__(self):
		'''
		Two API clients are the same if they use the same credentials. They must behave equally in respect to all the calls.
		:return: None
		'''
		return json.dumps([self.api_key, self.secret, self.customer_id])

	def __eq__(self, other):
		return str(self) == str(other)

	def __ne__(self, other):
		return str(self) != str(other)

	def __get_credentials(self, config_file_path):
		'''
		This method will try to interpret the file on the path in one of three ways:
		* first it will try to interpret it as an ini file (regardless of the file extension)
		* then it will try to interpret it as a JSON file (regardless of the file extension)
		* lastly it will try to interpret it as a Python file (file extension must be py)
		:param config_file_path: absolute path to the config file
		:return: api key, secret and customer id (tuple)
		'''
		api_key = None
		secret = None
		customer_id = None

		# All of the following tries catch all exceptions that can occur (as there are plenty): missing file,
		# wrong type, misconfigured.
		try:
			config_parser = ConfigParser()
			config_parser.read(config_file_path)
			api_key = config_parser.get('CONFIG', 'apiKey')
			secret = config_parser.get('CONFIG', 'secret')
			customer_id = config_parser.get('CONFIG', 'customerId')
			return api_key, secret, customer_id
		except:
			pass

		try:
			with open(config_file_path, 'rb') as file:
				blob = json.loads(file.read().decode())
				api_key = blob.get('apiKey')
				secret = blob.get('secret')
				customer_id = blob.get('customerId')
			return api_key, secret, customer_id
		except:
			pass

		# This is deprecated in python 3.4 (but it will work), so if working with later, try using ini or json approaches instead
		try:
			import importlib.machinery

			loader = importlib.machinery.SourceFileLoader('bitstamp.config', config_file_path)
			config = loader.load_module()

			api_key = config.api_key
			secret = config.secret
			customer_id = config.customer_id
			return api_key, secret, customer_id
		except:
			pass

		if api_key is None or secret is None:
			raise Exception('While the config file was found, it was not configured correctly. Check for examples here: {}'.format(EXAMPLES_URL))

		return api_key, secret, customer_id

	def __get_signature(self):
		'''
		Returns the signature for the next REST API call. nonce will be a timestamp (time.time()) multiplied by 1000,
		so we include some of the decimal part to reduce the chance of sending the same one more than once.
		:return: nonce, signature (tuple)
		'''
		nonce = str(int(time.time() * 1000))
		signature_raw = '{}{}{}'.format(nonce, self.customer_id, self.api_key)
		return nonce, hmac.new(self.secret.encode('utf8'), msg=signature_raw.encode('utf8'), digestmod=hashlib.sha256).hexdigest().upper()

	@staticmethod
	def __parse_ticker(blob):
		blob['timestamp'] = int(blob.get('timestamp'))
		blob['high'] = float(blob.get('high'))
		blob['ask'] = float(blob.get('ask'))
		blob['last'] = float(blob.get('last'))
		blob['low'] = float(blob.get('low'))
		blob['bid'] = float(blob.get('bid'))
		blob['volume'] = float(blob.get('volume'))
		blob['vwap'] = float(blob.get('vwap'))

		return blob

	def ticker(self, parsed=False):
		'''
		This method will call ticker resource and return the result.
		:param parsed: if True, blob will be parsed
		:return: ticker blob (dict)
		'''
		resource = 'ticker/'

		response = requests.get('{}{}'.format(self.api_endpoint, resource))

		if parsed:
			return self.__parse_ticker(json.loads(response.text))
		else:
			return json.loads(response.text)

	def order_book(self):
		'''
		This method will call order_book resource and return the result.
		:return: order book blob (dict)
		'''
		resource = 'order_book/'

		response = requests.get('{}{}'.format(self.api_endpoint, resource))

		return json.loads(response.text)

	def transactions(self, timespan='hour'):
		'''
		This method will call transactions resource and return the result.
		:param timespan: minute/hour string
		:return: list of transactions made in the past minute/hour
		'''
		resource = 'transactions/'

		if timespan != 'hour' and timespan != 'minute':
			raise Exception('Parameter time can be only "hour" or "minute". Default is "hour"')

		response = requests.get('{}{}'.format(self.api_endpoint, resource), data={
			'time': timespan
		})

		return json.loads(response.text)

	def eur_usd(self):
		'''
		This method will call eur_usd resource and return the result.
		:return: dict with the exchange rates between USD and EUR currencies
		'''
		resource = 'eur_usd/'

		response = requests.get('{}{}'.format(self.api_endpoint, resource))

		return json.loads(response.text)

	def balance(self):
		'''
		This method will call balance resource and return the result.
		This is a resource that requires signature.
		:return: a dict containing all the info about user account balance, BTC included
		'''
		resource = 'balance/'

		nonce, signature = self.__get_signature()

		response = requests.post('{}{}'.format(self.api_endpoint, resource), data={
			'key': self.api_key,
			'nonce': nonce,
			'signature': signature,
		})

		return json.loads(response.text)

	def user_transactions(self, offset=0, limit=100, sort='desc'):
		'''
		This method will call user_transactions resource and return the result.
		This is a resource that requires signature.
		:param offset: offset, useful for pagination, that has to be positive number
		:param limit: limit of how many transactions you will receive, in range (0, 1000]
		:param sort: one of the values: 'desc' or 'asc'
		:return: a list of user's transactions
		'''
		resource = 'user_transactions/'

		if offset < 0:
			raise Exception('Offset has to be a positive number')

		if limit < 1 or limit > 1000:
			raise Exception('Limit has to be a number from range [1, 1000]')

		if sort is not USER_TRANSACTION_ORDERING_ASC and sort is not USER_TRANSACTION_ORDERING_DESC:
			raise Exception('Sort parameter has to be one of {} or {}'.format(USER_TRANSACTION_ORDERING_DESC, USER_TRANSACTION_ORDERING_ASC))

		nonce, signature = self.__get_signature()

		response = requests.post('{}{}'.format(self.api_endpoint, resource), data={
			'key': self.api_key,
			'nonce': nonce,
			'signature': signature,
			'offset': offset,
			'limit': limit,
			'sort': sort,
		})

		return json.loads(response.text)

	def open_orders(self):
		'''
		This method will call open_orders resource and return the result.
		This is a resource that requires signature.
		:return: a list of dictionaries that represent orders that haven't been closed yet
		'''
		resource = 'open_orders/'

		nonce, signature = self.__get_signature()

		response = requests.post('{}{}'.format(self.api_endpoint, resource), data={
			'key': self.api_key,
			'nonce': nonce,
			'signature': signature,
		})

		return json.loads(response.text)

	def order_status(self, order_id):
		'''
		This method will call order_status resource and return the result.
		This is a resource that requires signature.
		:return: a dictionary that represent order current status and the transactions that have acted upon it
		'''
		resource = 'order_status/'

		nonce, signature = self.__get_signature()

		response = requests.post('{}{}'.format(self.api_endpoint, resource), data={
			'key': self.api_key,
			'nonce': nonce,
			'signature': signature,
			'id': order_id,
		})

		return json.loads(response.text)

	def buy_limit_order(self, amount, price, limit_price=None):
		'''
		This method will call buy resource and return the result.
		This is a resource that requires signature.
		This method will throw exception if amount * price yields a float that's less than 5
		:param amount: a float, the will be rounded to 8 decimal places, has to be positive
		:param price:  a float that will be rounded to 2 decimal places, has to be positive
		:param limit_price: a float that will be rounded to 2 decimal places, has to be positive
		:return: a boolean value, True if the order has been successfully opened, False if it failed
		'''
		resource = 'buy/'

		if amount < 0:
			raise Exception('Amount has to be a positive float')

		if price < 0:
			raise Exception('Price has to be a positive float')

		if (price * amount) < 5:
			raise Exception('Order volume (price * amount) has to be at least 5$')

		nonce, signature = self.__get_signature()

		data = {
			'key': self.api_key,
			'nonce': nonce,
			'signature': signature,
			'price': '{:.2f}'.format(price),
			'amount': '{:.8f}'.format(amount),
		}

		if limit_price is not None:
			if limit_price < 0:
				raise Exception('Limit price has to be a positive float')

			if (limit_price * amount) < 5:
				raise Exception('Order volume (limit_price * amount) has to be at least 5$')

			data['limit_price'] = limit_price

		response = requests.post('{}{}'.format(self.api_endpoint, resource), data=data)

		return json.loads(response.text)

	def sell_limit_order(self, amount, price, limit_price=None):
		'''
		This method will call sell resource and return the result.
		This is a resource that requires signature.
		This method will throw exception if amount * price yields a float that's less than 5
		:param amount: a float, the will be rounded to 8 decimal places, has to be positive
		:param price:  a float that will be rounded to 2 decimal places, has to be positive
		:param limit_price: a float that will be rounded to 2 decimal places, has to be positive
		:return: a boolean value, True if the order has been successfully opened, False if it failed
		'''
		resource = 'sell/'

		if amount < 0:
			raise Exception('Amount has to be a positive float')

		if price < 0:
			raise Exception('Price has to be a positive float')

		if (price * amount) < 5:
			raise Exception('Order volume (price * amount) has to be at least 5$')

		nonce, signature = self.__get_signature()

		data = {
			'key': self.api_key,
			'nonce': nonce,
			'signature': signature,
			'price': '{:.2f}'.format(price),
			'amount': '{:.8f}'.format(amount),
		}

		if limit_price is not None:
			if limit_price < 0:
				raise Exception('Limit price has to be a positive float')

			if (limit_price * amount) < 5:
				raise Exception('Order volume (limit_price * amount) has to be at least 5$')

			data['limit_price'] = limit_price

		response = requests.post('{}{}'.format(self.api_endpoint, resource), data=data)

		return json.loads(response.text)

	def cancel_order(self, order_id):
		'''
		This method will call buy cancel_order and return the result.
		This is a resource that requires signature.
		:param order_id: integer or string if the order's ID (can be found via open_orders method)
		:return: a boolean value, True if the order has been successfully closed, False if it failed
		'''
		resource = 'cancel_order/'

		if order_id is None:
			raise Exception('You have to provide an order id (you can get the list of open orders with open_roders())')

		nonce, signature = self.__get_signature()

		response = requests.post('{}{}'.format(self.api_endpoint, resource), data={
			'key': self.api_key,
			'nonce': nonce,
			'signature': signature,
			'id': order_id,
		})

		return json.loads(response.text)

	def withdrawal_requests(self):
		'''
		This method will call withdrawal_requests and return the result.
		This is a resource that requires signature.
		:return: a list of dictionaries, each representing one withdrawal request
		'''
		resource = 'withdrawal_requests/'

		nonce, signature = self.__get_signature()

		response = requests.post('{}{}'.format(self.api_endpoint, resource), data={
			'key': self.api_key,
			'nonce': nonce,
			'signature': signature,
		})

		return json.loads(response.text)

	def bitcoin_withdrawal(self, amount, address):
		'''
		This method will call bitcoin_withdrawal and return the result.
		This is a resource that requires signature.
		:param amount: a positive number, BTC amount for withdrawal
		:param address: a wallet address, a string that's longer than 25 characters and shorter than 35 characters
		:return: a boolean if withdrawal was successful and false if it failed
		'''
		resource = 'bitcoin_withdrawal/'

		if amount <= 0:
			raise Exception('Amount has to be a positive float')

		if address is None or address.strip() == '' or len(address) < 25 or len(address) > 34:
			raise Exception('You need to specify a valid address to which you want to send your BTC')

		nonce, signature = self.__get_signature()

		response = requests.post('{}{}'.format(self.api_endpoint, resource), data={
			'key': self.api_key,
			'nonce': nonce,
			'signature': signature,
			'amount': '{:.8f}'.format(amount),
			'address': address,
		})

		return json.loads(response.text)

	def unconfirmed_bitcoin_deposits(self):
		'''
		This method will call bitcoin_withdrawal and return the result.
		This is a resource that requires signature.
		:return:a list of pending BTC deposits to your wallet
		'''
		resource = 'unconfirmed_btc/'

		nonce, signature = self.__get_signature()

		response = requests.post('{}{}'.format(self.api_endpoint, resource), data={
			'key': self.api_key,
			'nonce': nonce,
			'signature': signature,
		})

		return json.loads(response.text)

	def wallet_address(self):
		'''
		This method will call bitcoin_withdrawal and return the result.
		This is a resource that requires signature.
		:return: a string representing your wallet address
		'''
		resource = 'bitcoin_deposit_address/'

		nonce, signature = self.__get_signature()

		response = requests.post('{}{}'.format(self.api_endpoint, resource), data={
			'key': self.api_key,
			'nonce': nonce,
			'signature': signature,
		})

		return json.loads(response.text)

	def __on_open(self, channel):
		channel_string = self.ws_channels[channel]
		def open_channel(internal_ws):
			return internal_ws.send(channel_string)

		return open_channel

	def __generic_error_callback(self, *args, **kwargs):
		pass

	def __generic_close_callback(self, *args, **kwargs):
		pass

	def attach_ws(self, channel, callback, error_callback=None, close_callback=None):
		'''
		This method lets you attach a callback or callbacks to a specific channel that will react each time web socket
		gets a message.
		:param channel: one of bitstamp.WS_CHANNEL_LIVE_TRADES, bitstamp.WS_CHANNEL_ORDER_BOOK or bitstamp.WS_CHANNEL_ORDER_BOOK_DIFF
		:param callback: a method that will react to the message received on the web socket
		:param error_callback: optional handler for errors
		:param close_callback: optional handler for close event
		:return: None
		'''
		if error_callback is None:
			error_callback = self.__generic_error_callback

		if close_callback is None:
			close_callback = self.__generic_close_callback

		self.ws = websocket.WebSocketApp(self.websockets_endpoint,
			on_message=self.__data_message_closure(callback),
			on_error=error_callback,
			on_close=close_callback
		)
		self.ws.on_open = self.__on_open(channel)
		self.ws.run_forever()

	def close_ws(self):
		'''
		Closes an open web socket
		:return:
		'''
		if self.ws:
			self.ws.close()
		else:
			raise Exception('Web socket hasn\'t been opened yet')

	def __data_message_closure(self, callback):
		# Send through only those messages that actually have any relevant data
		def on_message(ws, message):
			message = json.loads(message)
			if message.get('event') in self.ws_data_events:
				callback(json.loads(message.get('data')))

		return on_message

	@staticmethod
	def parse_datetime(string):
		'''
		Convenience method that parses datetime objects found in results of the API
		:param string: formatted datetime
		:return: datetime object parsed from the passed string
		'''
		return datetime.strptime(string, BITSTAMP_DATETIME_FORMAT)

