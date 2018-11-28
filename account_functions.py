import json
import web3
import requests
import time
from web3 import Web3

from amp_python_client.constants import rest_endpoints
import hash_lib

class ampRestEndpoints(object): #init class with ETH account address
    def __init__(self, _base_endpoint, _user_address, _private_key=None, web3_endpoint=None):
        self.base_endpoint = _base_endpoint

        self.exchangeAddress = '0x2768f1543ec9145cb680fc9699672c1a3226346d'
        self.tokens = self.getRegisteredTokens()

        self._user_address = _user_address
        self._private_key = _private_key

        self._start_nonce = None
        self._start_time = int(time.time() * 1000)

        self.web3 = Web3(Web3.HTTPProvider(web3_endpoint))


    def _post(self, path, signed=False, **kwargs):
        return self._request('post', path, signed, **kwargs)

    # ACCOUNT METHODS

    def _get_nonce(self):
        return self._start_nonce + int(time.time() * 1000) - self._start_time

    def getAllPairs(self):
        pair_endpoint = rest_endpoints.GET_ALL_PAIRS
        uri = self.base_endpoint + pair_endpoint
        return requests.get(uri).json()

    def getRegisteredTokens(self):
        token_endpoint = rest_endpoints.GET_REGISTERED_TOKENS
        uri = self.base_endpoint + token_endpoint
        return requests.get(uri).json()

    def getCoinAddress(self, coin):
        address_list = self.tokens['data']
        address = None
        for i in address_list:
            if i['symbol'] == str(coin):
                address = str(i['contractAddress'])
                break
        return address

    def get_balances(self, token=None):
        token_endpoint = rest_endpoints.GET_TOKENS_AT_ADDRESS.format(address = self._user_address)
        uri = self.base_endpoint + token_endpoint
        balances = requests.get(uri).json()

        '''
        balances = balances['data']

        if token:
            if balances:
                for i in balances:
                    if i['token'] == token: # correct later
                        balances = i['balance'] # correct later
        '''

        return balances

    # return trades. Filter by pair or buy/sell
    def get_trades(self, pair=None, side=None):
        order_endpoint = rest_endpoints.GET_ALL_FILLED_ORDERS_ON_ADDRESS.format(address = self._user_address)
        uri = self.base_endpoint + order_endpoint
        trades = requests.get(uri).json()

        if pair:
            if trades:
                trades_in_pair = []
                coins = list(map(str, pair.split('/')))
                coin1 = coins[0]
                coin2 = coins[1]
                for i in trades:
                    if (i['baseToken'] == coin1) and (i['quoteToken'] == coin2):
                        trades_in_pair.append(i)
                trades = trades_in_pair

        if side:
            if trades:
                if side == 'BUY':
                    directional_trades = []
                    for i in trades:
                        if i['side'] == 'BUY':
                            directional_trades.append(i)
                    trades = directional_trades
                elif side == 'SELL':
                    directional_trades = []
                    for i in trades:
                        if i['side'] == 'SELL':
                            directional_trades.append(i)
                    trades = directional_trades

        return trades

    # ORDER METHODS

    #Cancel an order through orderHash
    def cancel_order(self, orderHash):
        coins = list(map(str, pair.split('/')))
        coin1 = coins[0]
        coin2 = coins[1]

        orderCancel = {}

        orderCancel['orderHash'] = orderHash
        orderCancel['hash'] = getOrderCancelHash(orderCancel)

        orderCancel = signOrder(orderCancel)
        return orderCancel

    #Cancel all orders
    def cancel_all_orders(self):
        orders = self.get_open_orders(self._user_address)
        if orders:
            for i in orders:
                self.cancel_order(i['orderHash'])

        return orders

    #Get list of all open orders for an address. Can be filtered by pair or by BUY/SELL
    def get_open_orders(self, pair=None, side=None): # PAIR format = 'pair1/pair2', ex: 'ZRX/WETH'. Optional to get open orders for a just a particular pair
        order_endpoint = rest_endpoints.GET_ALL_ORDERS_ON_ADDRESS.format(address=self._user_address)
        uri = self.base_endpoint + order_endpoint
        orders = requests.get(uri).json()

        open_orders = []
        if orders:
            all_open_orders = []
            for i in orders:
                if i['status'] == 'OPEN':
                    all_open_orders.append(i)
            open_orders = all_open_orders

            if pair:
                if open_orders:
                    orders_for_pair = []
                    coins = list(map(str, pair.split('/')))
                    coin1 = coins[0]
                    coin2 = coins[1]
                    for i in open_orders:
                        if (i['baseToken'] == coin1) and (i['quoteToken'] == coin2):
                            orders_for_pair.append(i)
                    open_orders = orders_for_pair

            if side:
                if open_orders:
                    if side == 'BUY':
                        directional_orders = []
                        for i in open_orders:
                            if i['side'] == 'BUY':
                                directional_orders.append(i)
                        open_orders = directional_orders
                    elif side == 'SELL':
                        directional_orders = []
                        for i in open_orders:
                            if i['side'] == 'SELL':
                                directional_orders.append(i)
                        open_orders = directional_orders

        return open_orders

    def place_limit_order(self, pair, side, quantity, price):
        dec_format = '{0:.8f}'
        order_price = dec_format.format(float(price))

        coins = list(map(str, pair.split('/')))
        coin1 = coins[0]
        coin2 = coins[1]
        coin1_address = self.getCoinAddress(coin=coin1)
        coin2_address = self.getCoinAddress(coin=coin2)

        order = {}
        order['side'] = side
        order['amount'] = str(quantity)
        order['price'] = str(order_price)
        order["makeFee"] = 0
        order["takeFee"] = 0 
        order['baseToken'] = coin1_address if side =='BUY' else coin2_address
        order['quoteToken'] = coin2_address if side == 'BUY' else coin1_address
        order['exchangeAddress'] = self.exchangeAddress

        order['userAddress'] = self._user_address

        order["nonce"] = getRandomNonce() 
        order["hash"] = getOrderHash(order)

        #Sign & send
        try:
            signed = web3.eth.account.signTransaction(order, self._private_key)
            web3.eth.sendRawTransaction(signed.rawTransaction)
        except:
            order = 'Couldnt place order: Check private key'

        return order

    #def place_market_order(self, pair, side, quantity, limit=0):


    #MARKET METHODS

    def get_all_pairs(self): # taken from amp-python-api-client
        pair_endpoint = rest_endpoints.GET_ALL_PAIRS
        uri = self.base_endpoint + pair_endpoint
        return requests.get(uri).json()

    #Get bids and asks for given pair
    def get_order_book(self, pair): # pair format = 'pair1/pair2', ex: 'ZRX/WETH'
        coins = list(map(str, pair.split('/')))
        coin1 = coins[0]
        coin2 = coins[1]

        ob_endpoint = rest_endpoints.GET_FULL_ORDERBOOK_ON_PAIR.format(baseToken = self.addresses[coin1], quoteToken = self.addresses[coin2])
        uri = self.base_endpoint + ob_endpoint
        all_orders = requests.get(uri).json()

        bids = []
        asks = []
        for i in all_orders:
            if i['side'] == 'BUY':
                bids.append(i)
            else:
                asks.append(i)

        orders = {'bids': bids, 'asks': asks}
        return orders

    #OHLC data 
    #def get_OHLC_data(pair, timeframe): 
