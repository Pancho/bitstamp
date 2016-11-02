import unittest
import hashlib
import hmac
import os


from bitstamp import bitstamp


class TestInstantiation(unittest.TestCase):
	def setUp(self):
		self.api_key = 'some api key'
		self.secret = 'some secret'
		self.customer_id = 'some customer id'
		self.files = [
			'config.json',
			'config_reversed.json',
			'config_missing_api_key.json',
			'config_missing_secret.json',
			'config_misconfigured.json',
			'config.py',
			'config_reversed.py',
			'config_missing_api_key.py',
			'config_missing_secret.py',
			'config_misconfigured.py',
			'config_syntax_error.py',
			'config.ini',
			'config_reversed.ini',
			'config_missing_api_key.ini',
			'config_missing_secret.ini',
			'config_misconfigured.ini',
		]

		file = open('config.ini', 'wb')
		file.write(bytes('[CONFIG]\napikey={}\nsecret={}\ncustomerId={}'.format(self.api_key, self.secret, self.customer_id), encoding='utf8'))
		self.ini_path = os.path.abspath(file.name)
		file.close()

		file = open('config_reversed.ini', 'wb')
		file.write(bytes('[CONFIG]\nsecret={}\napikey={}\ncustomerId={}'.format(self.secret, self.api_key, self.customer_id), encoding='utf8'))
		self.ini_config_reversed_path = os.path.abspath(file.name)
		file.close()

		file = open('config_missing_api_key.ini', 'wb')
		file.write(bytes('[CONFIG]\nsecret={}\ncustomerId={}'.format(self.secret, self.customer_id), encoding='utf8'))
		self.ini_config_missing_api_key_path = os.path.abspath(file.name)
		file.close()

		file = open('config_missing_secret.ini', 'wb')
		file.write(bytes('[CONFIG]\napikey={}\ncustomerId={}'.format(self.api_key, self.customer_id), encoding='utf8'))
		self.ini_config_missing_secret_path = os.path.abspath(file.name)
		file.close()

		file = open('config_misconfigured.ini', 'wb')
		file.write(bytes('secret={}\napikey={}\ncustomerId={}'.format(self.secret, self.api_key, self.customer_id), encoding='utf8'))
		self.ini_config_misconfigured_path = os.path.abspath(file.name)
		file.close()

		file = open('config.json', 'wb')
		file.write(bytes('{{"apiKey": "{}", "secret": "{}", "customerId": "{}"}}'.format(self.api_key, self.secret, self.customer_id), encoding='utf8'))
		self.json_path = os.path.abspath(file.name)
		file.close()

		file = open('config_reversed.json', 'wb')
		file.write(bytes('{{"secret": "{}", "apiKey": "{}", "customerId": "{}"}}'.format(self.secret, self.api_key, self.customer_id), encoding='utf8'))
		self.json_config_reversed_path = os.path.abspath(file.name)
		file.close()

		file = open('config_missing_api_key.json', 'wb')
		file.write(bytes('{{"secret": "{}", "customerId": "{}"}}'.format(self.secret, self.customer_id), encoding='utf8'))
		self.json_config_missing_api_key_path = os.path.abspath(file.name)
		file.close()

		file = open('config_missing_secret.json', 'wb')
		file.write(bytes('{{"apiKey": "{}", "customerId": "{}"}}'.format(self.api_key, self.customer_id), encoding='utf8'))
		self.json_config_missing_secret_path = os.path.abspath(file.name)
		file.close()

		file = open('config_misconfigured.json', 'wb')
		file.write(bytes('{{\'apiKey\': \'{}\', \'secret\': \'{}\', \'customerId\': \'{}\'}}'.format(self.secret, self.api_key, self.customer_id), encoding='utf8'))
		self.json_config_misconfigured_path = os.path.abspath(file.name)
		file.close()

		file = open('config.py', 'wb')
		file.write(bytes('api_key = \'{}\'\nsecret = \'{}\'\ncustomer_id = \'{}\''.format(self.api_key, self.secret, self.customer_id), encoding='utf8'))
		self.py_path = os.path.abspath(file.name)
		file.close()

		file = open('config_reversed.py', 'wb')
		file.write(bytes('secret = \'{}\'\napi_key = \'{}\'\ncustomer_id = \'{}\''.format(self.secret, self.api_key, self.customer_id), encoding='utf8'))
		self.py_config_reversed_path = os.path.abspath(file.name)
		file.close()

		file = open('config_missing_api_key.py', 'wb')
		file.write(bytes('secret = \'{}\'\ncustomer_id = \'{}\''.format(self.secret, self.customer_id), encoding='utf8'))
		self.py_config_missing_api_key_path = os.path.abspath(file.name)
		file.close()

		file = open('config_missing_secret.py', 'wb')
		file.write(bytes('api_key = \'{}\'\ncustomer_id = \'{}\''.format(self.api_key, self.customer_id), encoding='utf8'))
		self.py_config_missing_secret_path = os.path.abspath(file.name)
		file.close()

		file = open('config_misconfigured.py', 'wb')
		file.write(bytes('api_key = {}\nsecret = {}\ncustomer_id = {}'.format(self.secret, self.api_key, self.customer_id), encoding='utf8'))
		self.py_config_misconfigured_path = os.path.abspath(file.name)
		file.close()

		self.working_api = bitstamp.Bitstamp(api_key=self.api_key, secret=self.secret, customer_id=self.customer_id)

	def test_instantiate_no_params(self):
		self.assertRaises(Exception, lambda: bitstamp.Bitstamp(), msg='Not pasing any arguments to the constructor should raise an exception')

	def test_instantiate_only_api_key(self):
		self.assertRaises(Exception, lambda: bitstamp.Bitstamp(None, self.api_key, None, self.customer_id), msg='Not passing secret, expecting exception')

	def test_instantiate_only_secret(self):
		self.assertRaises(Exception, lambda: bitstamp.Bitstamp(None, None, self.secret, self.customer_id), msg='Not passing api key, expecting exception')

	def test_instantiate_only_customer_id(self):
		self.assertRaises(Exception, lambda: bitstamp.Bitstamp(None, None, None, self.customer_id), msg='Not passing customer, expecting exception')

	def test_instantiate_ini(self):
		self.assertEqual(self.working_api, bitstamp.Bitstamp(self.ini_path))

	def test_instantiate_ini_reversed(self):
		self.assertEqual(self.working_api, bitstamp.Bitstamp(self.ini_config_reversed_path))

	def test_instantiate_ini_missing_api_key(self):
		self.assertRaises(Exception, lambda: bitstamp.Bitstamp(self.ini_config_missing_api_key_path), msg='Not passing api key, expecting exception')

	def test_instantiate_ini_missing_secret(self):
		self.assertRaises(Exception, lambda: bitstamp.Bitstamp(self.ini_config_missing_secret_path), msg='Not passing secret, expecting exception')

	def test_instantiate_ini_misconfigured(self):
		self.assertRaises(Exception, lambda: bitstamp.Bitstamp(self.ini_config_misconfigured_path), msg='Passing a config that\'s misconfigured should raise an exception')

	def test_instantiate_json(self):
		self.assertEqual(self.working_api, bitstamp.Bitstamp(self.json_path))

	def test_instantiate_json_reversed(self):
		self.assertEqual(self.working_api, bitstamp.Bitstamp(self.json_config_reversed_path))

	def test_instantiate_json_missing_api_key(self):
		self.assertRaises(Exception, lambda: bitstamp.Bitstamp(self.json_config_missing_api_key_path), msg='Not passing api key, expecting exception')

	def test_instantiate_json_missing_secret(self):
		self.assertRaises(Exception, lambda: bitstamp.Bitstamp(self.json_config_missing_secret_path), msg='Not passing secret, expecting exception')

	def test_instantiate_json_misconfigured(self):
		self.assertRaises(Exception, lambda: bitstamp.Bitstamp(self.json_config_misconfigured_path), msg='Passing a config that\'s misconfigured should raise an exception')

	def test_instantiate_py(self):
		self.assertEqual(self.working_api, bitstamp.Bitstamp(self.py_path))

	def test_instantiate_py_reversed(self):
		self.assertEqual(self.working_api, bitstamp.Bitstamp(self.py_config_reversed_path))

	def test_instantiate_py_missing_api_key(self):
		self.assertRaises(Exception, lambda: bitstamp.Bitstamp(self.py_config_missing_api_key_path), msg='Not passing api key, expecting exception')

	def test_instantiate_py_missing_secret(self):
		self.assertRaises(Exception, lambda: bitstamp.Bitstamp(self.py_config_missing_secret_path), msg='Not passing secret, expecting exception')

	def test_instantiate_py_misconfigured(self):
		self.assertRaises(Exception, lambda: bitstamp.Bitstamp(self.py_config_misconfigured_path), msg='Passing a config that\'s misconfigured should raise an exception')

	def tearDown(self):
		for file_path in self.files:
			if os.path.isfile(file_path):
				os.remove(file_path)


class TestSignature(unittest.TestCase):
	def setUp(self):
		self.api_key = 'some api key'
		self.secret = 'some secret'
		self.customer_id = 'some customer id'
		self.working_api = bitstamp.Bitstamp(api_key=self.api_key, secret=self.secret, customer_id=self.customer_id)

	def test_signature(self):
		nonce, signature = self.working_api._Bitstamp__get_signature()

		# Construct the signature per instructions from the official API page
		signature_raw = '{}{}{}'.format(nonce, self.customer_id, self.api_key)
		new_signature = hmac.new(self.secret.encode('utf8'), msg=signature_raw.encode('utf8'), digestmod=hashlib.sha256).hexdigest().upper()

		self.assertEqual(new_signature, signature, msg='Signatures should match (from client: {} VS from test: {})'.format(signature, new_signature))

	def tearDown(self):
		pass


# One should not run this test suite too many times, as they still use regular API calls and can still
# cause a ban for 15 minutes.
class TestUnsignedCalls(unittest.TestCase):
	def setUp(self):
		self.api_key = 'some api key'
		self.secret = 'some secret'
		self.customer_id = 'some customer id'
		self.working_api = bitstamp.Bitstamp(api_key=self.api_key, secret=self.secret, customer_id=self.customer_id)

	def test_ticker(self):
		# No real need to sort these, but to be sure we use the same ordering, we should use the same order function
		expected_keys = sorted([
			'timestamp',
			'high',
			'ask',
			'last',
			'low',
			'open',
			'bid',
			'volume',
			'vwap',
		])

		for pair in bitstamp.ALL_PAIRS:
			ticker_blob = self.working_api.ticker(currency=pair)
			ticker_blob_parsed = self.working_api.ticker(parsed=True)

			self.assertIsNotNone(ticker_blob, msg='Result should not be none')
			self.assertTrue(isinstance(ticker_blob, dict), msg='Result from this api call has to be a python dictionary (even if there\' an error on the SPI server)')

			keys = sorted(list(ticker_blob.keys()))
			self.assertEqual(keys, expected_keys, msg='Expected keys don\'t match with the received ones')

			# If we just return the parsed JSON from the API, all the values should be strings
			# ADDENDUM: I have commented out this test in particular, because open parameter (open) is not of type string
			# (for some reason)
			# for key, value in ticker_blob.items():
			# 	self.assertTrue(isinstance(value, str), msg='{} is not of type string, but should be'.format(key))

			# If we parse the results' values, none of them should be strings
			for key, value in ticker_blob_parsed.items():
				self.assertFalse(isinstance(value, str), msg='{} is of type string, but should not be be'.format(key))


	def test_order_book(self):
		# No real need to sort these, but to be sure we use the same ordering, we should use the same order function
		expected_keys = sorted([
			'timestamp',
			'asks',
			'bids',
		])

		for pair in bitstamp.ALL_PAIRS:
			order_book = self.working_api.order_book(currency=pair)

			self.assertIsNotNone(order_book, msg='Result should not be none')
			self.assertTrue(isinstance(order_book, dict), msg='Result from this api call has to be a python dictionary (even if there\' an error on the SPI server)')

			keys = sorted(list(order_book.keys()))
			self.assertEqual(keys, expected_keys, msg='Expected keys don\'t match with the received ones')

	def test_transactions(self):
		# We don't need hour's worth of transactions to perform tests
		for pair in bitstamp.ALL_PAIRS:
			transactions = self.working_api.transactions(currency=pair, timespan='minute')

			self.assertIsNotNone(transactions, msg='Result should not be none')
			self.assertTrue(isinstance(transactions, list), msg='Result from this api call has to be a python list (even if there\' an error on the SPI server)')

	def tearDown(self):
		pass


class TestSignedValidatedCalls(unittest.TestCase):
	'''
	These calls have to be signed and will return exceptions from the API, however there are some validations
	performed before that happens and we should test for those. API exceptions will not break the runtime, but
	validations in this API client will try to.

	Methods that are validated are:
	* buy_limit_order
	* sell_limit_order
	* user_transactions
	* cancel_order
	* bitcoin_withdrawal
	'''
	def setUp(self):
		self.api_key = 'some api key'
		self.secret = 'some secret'
		self.customer_id = 'some customer id'
		self.working_api = bitstamp.Bitstamp(api_key=self.api_key, secret=self.secret, customer_id=self.customer_id)

	def test_buy_limit_order_validations(self):
		self.assertRaises(Exception, lambda: self.working_api.buy_limit_order(-1, 1, None), msg='Amount should be capped at min=0')
		self.assertRaises(Exception, lambda: self.working_api.buy_limit_order(1, -1, None), msg='Price should be capped at min=0')
		self.assertRaises(Exception, lambda: self.working_api.buy_limit_order(5, 0.9999, None), msg='The volume of the order should be 5$ or more')
		self.assertRaises(Exception, lambda: self.working_api.buy_limit_order(5, 2, -1), msg='Limit price if bought should be capped at min=0')

	def test_sell_limit_order_validations(self):
		self.assertRaises(Exception, lambda: self.working_api.sell_limit_order(-1, 1, None), msg='Amount should be capped at min=0')
		self.assertRaises(Exception, lambda: self.working_api.sell_limit_order(1, -1, None), msg='Price should be capped at min=0')
		self.assertRaises(Exception, lambda: self.working_api.sell_limit_order(5, 0.9999, None), msg='The volume of the order should be 5$ or more')
		self.assertRaises(Exception, lambda: self.working_api.sell_limit_order(5, 2, -1), msg='Limit price if sold should be capped at min=0')

	def test_user_transactions_validations(self):
		self.assertRaises(Exception, lambda: self.working_api.user_transactions(-1, 1, 'desc'), msg='Offset has to be capped at min=0')
		self.assertRaises(Exception, lambda: self.working_api.user_transactions(0, 0, 'desc'), msg='Limit should be capped at min=1')
		self.assertRaises(Exception, lambda: self.working_api.user_transactions(0, 1001, 'desc'), msg='Limit should be capped at max=1000')
		self.assertRaises(Exception, lambda: self.working_api.user_transactions(0, 1, 'not-asc-or-desc'), msg='Ordering should either be "desc" or "asc"')

	def test_cancel_order_validations(self):
		self.assertRaises(Exception, lambda: self.working_api.cancel_order(None), msg='Order id must not be None')

	def test_bitcoin_withdrawal_validations(self):
		self.assertRaises(Exception, lambda: self.working_api.bitcoin_withdrawal(0, '123456789012345678901234567890'), msg='Amount should be capped at min>0')
		self.assertRaises(Exception, lambda: self.working_api.bitcoin_withdrawal(1, '1'), msg='Address string should be long at least 25 characters')
		self.assertRaises(Exception, lambda: self.working_api.bitcoin_withdrawal(1, '12345678901234567890123456789012345'), msg='Address string should be long less than 35 characters')

	def tearDown(self):
		pass


# class TestWebSocketsLiveTrades(unittest.TestCase):
# 	def setUp(self):
# 		self.api_key = 'some api key'
# 		self.secret = 'some secret'
# 		self.customer_id = 'some customer id'
# 		self.working_api = bitstamp.Bitstamp(api_key=self.api_key, secret=self.secret, customer_id=self.customer_id)
#
# 	def message_closure(self):
# 		def test_message(message):
# 			expected_keys = sorted([
# 				'amount',
# 				'price',
# 				'id',
# 			])
# 			keys = sorted(list(message.keys()))
# 			self.assertEqual(keys, expected_keys, msg='Expected keys don\'t match with the received ones')
# 			self.working_api.close_ws()
#
# 		return test_message
#
# 	def test_live_trades(self):
# 		self.working_api.attach_ws(bitstamp.WS_CHANNEL_LIVE_TRADES, self.message_closure())
#
# 	def tearDown(self):
# 		pass
#
#
# class TestWebSocketsOrderBook(unittest.TestCase):
# 	def setUp(self):
# 		self.api_key = 'some api key'
# 		self.secret = 'some secret'
# 		self.customer_id = 'some customer id'
# 		self.working_api = bitstamp.Bitstamp(api_key=self.api_key, secret=self.secret, customer_id=self.customer_id)
#
# 	def message_closure(self):
# 		def test_message(message):
# 			expected_keys = sorted([
# 				'asks',
# 				'bids',
# 			])
# 			keys = sorted(list(message.keys()))
# 			self.assertEqual(keys, expected_keys, msg='Expected keys don\'t match with the received ones')
# 			self.working_api.close_ws()
#
# 		return test_message
#
# 	def test_live_trades(self):
# 		self.working_api.attach_ws(bitstamp.WS_CHANNEL_ORDER_BOOK, self.message_closure())
#
# 	def tearDown(self):
# 		pass
#
#
# class TestWebSocketsOrderBookDiff(unittest.TestCase):
# 	def setUp(self):
# 		self.api_key = 'some api key'
# 		self.secret = 'some secret'
# 		self.customer_id = 'some customer id'
# 		self.working_api = bitstamp.Bitstamp(api_key=self.api_key, secret=self.secret, customer_id=self.customer_id)
#
# 	def message_closure(self):
# 		def test_message(message):
# 			expected_keys = sorted([
# 				'asks',
# 				'bids',
# 				'timestamp',
# 			])
# 			keys = sorted(list(message.keys()))
# 			self.assertEqual(keys, expected_keys, msg='Expected keys don\'t match with the received ones')
# 			self.working_api.close_ws()
#
# 		return test_message
#
# 	def test_live_trades(self):
# 		self.working_api.attach_ws(bitstamp.WS_CHANNEL_ORDER_BOOK_DIFF, self.message_closure())
#
# 	def tearDown(self):
# 		pass
