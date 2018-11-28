from client_amp import AmpClient
from data_calculations import *
from arbitrage_functions import *
from b_data import load_dataframe, coin_quote, get_all_tickers

import pandas as pd
import numpy as np
import time
import datetime
from random import randint

client = AmpClient('0x66CE2a9B124cF5645b14F47aa9CE9631525a31E0')

class Bot:
    def __init__(self):
        self.base_coins = ('USDC', 'DAI', 'WETH')
        _tokens = []

        workable_tokens = client.tokens['data']
        for i in workable_tokens:
            if str(i['symbol']) not in self.base_coins:
                _tokens.append(str(i['symbol']))

        _pairs = []
        for c in self.base_coins:
            for i in _tokens:
                pair = str(i) + '/' + str(c)
                _pairs.append(pair)

        binance_pairs = []
        b_tickers = get_all_tickers()
        for i in b_tickers:
            if 'ETH' in str(i['symbol']):
                binance_pairs.append(i['symbol'])

        self._tokens = _tokens
        self._pairs = _pairs
        self.binance_pairs = binance_pairs

        self._start_time = int(time.time())
        self._quote_refresh_interval = 20 # Frequency the bids/ask refresh for the faster time frame bot

        self._quote_refresh_interval2 = 600 # Frequency the bids/ask refresh for the slower time frame bot. Set 'OFF' to turn off slower time frame bot
        self._data_refresh_interval = 300 # Frequency at which the bot will collect market data to help with calculations. Set 'OFF' to turn off

        self._position_size1 = 5 # (ETH) amount to offer/bid
        self._position_size2 = 22 # (ETH) amount to offer/bid for slower moving bot

        self.spread_1 = 0.0022
        self.spread_2 = 3 # Spread multipler for the slower bot. This number, times spread_1

        self.arbitrage = 'ON' #turn arbitrage on or off

        self._max_position = 20 #max amount of inventory if arbitrage off (ETH)

        self._bot_duration = 999999999999 # Optional: time the bot stays running.

    def start(self):
        # Set file path for activity files

        stats_file = 'MarketMaking_Activity_Stats.csv'
        tokens_file = 'MarketMaking_Token_Stats.csv'


        # This is for working with the binance pairs and can be ignored.
        #------------------------------------
        five = ('LTCETH', 'DASHETH', 'XMRETH', 'BCCETH', 'ZECETH', 'REPETH')
        six = ('BNBETH', 'ETCETH', 'QTUMETH', 'MCOETH', 'MTLETH', 'NEOETH', 'ARKETH', 'LSKETH', 'OMGETH', 'TRIGETH', 'EOSETH', 'STRATETH', 'BTGETH', 'KMDETH', 
            'ONTETH', 'PPTETH', 'WANETH', 'NASETH', 'BNTETH', 'NANOETH', 'STEEMETH', 'WAVESETH', 'WTCETH', 'AEETH', 'ICXETH', 'AIONETH')
        seven = ('OAXETH', 'GRSETH', 'ARNETH', 'VIBEETH')
        eight = (
            'ADAETH', 'XLMETH', 'XRPETH', 'ELFETH', 'FUNETH', 'BCPTETH', 'SNGLSETH', 'DENTETH', 'XVGETH', 'ZRXETH', 'QKCETH', 
            'MANAETH', 'XEMETH', 'GTOETH', 'IOTAETH', 'LOOMETH', 'SNMETH', 'NULSETH', 'MFTETH', 'TRXETH', 'VETETH', 'ZILETH', 
            'QLCETH', 'DNTETH', 'KEYETH', 'CMTETH', 'PHXETH', 'STORMETH', 'IOTXETH', 'ENJETH', 'LENDETH', 'POEETH', 'DOCKETH',
            'CHATETH', 'CNDETH', 'TNTETH', 'WPRETH', 'MTHETH', 'PAXETH', 'SNTETH', 'NPXSETH', 'LRCETH') 

        zero = ('ADA', 'ADX', 'AMB', 'APPC', 'ARN', 'BAT', 'BCPT', 'BQX', 'BRD', 'BTS', 'CMT', 'CVC', 'ENG', 'EVX', 'GNT', 'GRS', 'XLM', 'XRP', 'ELF', 'XVG', 
            'FUN', 'ZRX', 'DENT', 'QKC', 'SNGLS', 'XEM', 'KNC', 'BCPT', 'GTO', 'IOTA', 'LOOM', 'NULS', 'MFT', 'TRX', 'VET', 'ZIL', 'QLC', 'SNM', 'KNC', 'LINK', 
            'MANA', 'MDA', 'PAX', 'POWR', 'RDN', 'SUB', 'SYS', 'THETA', 'DNT', 'KEY', 'OAX', 'STORM', 'PAX', 'PHX', 'IOTX', 'ENJ', 'LEND', 'POE', 'POA', 'DATA', 'DOCK',
            'CHAT', 'CND', 'VIBE', 'TNT', 'WPR', 'MTH', 'LRC', 'SNT', 'NPXS', 'LRC', 'MKR', 'PRFT')
        two = ('BNB', 'ETC', 'QTUM', 'MCO', 'MTL', 'NEO', 'LSK', 'OMG', 'ARK', 'EOS', 'STRAT', 'TRIG', 'BTG', 'KMD', 'ONT', 'PPT', 'WAN', 'NAS', 'LTC', 'DASH', 
            'XMR', 'BCC', 'ZEC', 'REP', 'NANO', 'BNT', 'AE', 'CLOAK', 'ICX', 'GXS', 'GVT', 'LUN', 'NXS', 'WAVES', 'WTC', 'DGD', 'STEEM', 'AION')
        #------------------------------------


        # dataframe to keep track of activity

        stats_df = pd.DataFrame(columns=['Pair', 'Position', 'Total_Traded', 'Profit', 'Bid_OrderID', 'Bid_OrderID2', 'Offer_OrderID', 'Offer_OrderID2', 'Volatility', 'Commissions'])
        tokens_df = pd.DataFrame(columns=['Token', 'Start_Balance', 'Current_Balance', 'Total_Traded', 'Profit'])

        pair_list = np.asarray(self._pairs)
        token_list = np.asarray(self._tokens)

        for i in self.base_coins:
            np.append(token_list, i)

        stats_df['Pair'] = pair_list
        tokens_df['Token'] = token_list

        # It will try to load from a file if already exists (i.e. when the bot is restarted)
        try:
            stats_df = pd.read_csv(stats_file)
            tokens_df = pd.read_csv(tokens_file)

        except:
            for index, row in stats_df.iterrows():
                stats_df.at[index, 'Position'] = 0
                stats_df.at[index, 'Total_Traded'] = 0
                stats_df.at[index, 'Profit'] = 0
                stats_df.at[index, 'Bid_OrderID'] = 0
                stats_df.at[index, 'Bid_OrderID2'] = 0
                stats_df.at[index, 'Offer_OrderID'] = 0
                stats_df.at[index, 'Offer_OrderID2'] = 0
                stats_df.at[index, 'Volatility'] = 0
                stats_df.at[index, 'Commissions'] = 0

            for index, row in tokens_df.iterrows():

                current_balance = 0 #get_balances(token=str(row['Pair']))
                tokens_df.at[index, 'Start_Balance'] = current_balance
                tokens_df.at[index, 'Current_Balance'] = current_balance
                tokens_df.at[index, 'Total_Traded'] = 0
                tokens_df.at[index, 'Profit'] = 0

        try:
            stats_df.to_csv(stats_file, index=False)
            tokens_df.to_csv(tokens_file, index=False)
        except:
            pass

        stats_df.Position.astype('float')
        stats_df.Total_Traded.astype('float')
        stats_df.Profit.astype('float')
        stats_df.Volatility.astype('float')
        stats_df.Commissions.astype('float')

        print()
        print('PAIR STATS')
        print(stats_df)
        print()
        print('TOKENS')
        print(tokens_df)
        print()

        data_update_interval = self._start_time
        bot_slow = self._start_time

        while time.time() < self._start_time + 60 * int(self._bot_duration):

            #If commission coin required, add function here to top up

            print()
            print(datetime.datetime.now())
            print()

            for index, row in stats_df.iterrows():
                coins = list(map(str, row['Pair'].split('/')))
                coin1 = coins[0]
                coin2 = coins[1]
                if coin2 == 'WETH':
                    coin2 = 'ETH'

                bid_price = 'OFF'
                offer_price = 'OFF'

                spread_1 = self.spread_1

                b_pair = str(coin1) + str(coin2)
                print('Scanning ' + str(b_pair) + ' data...')

                if b_pair in five:
                    decimal_places = 5
                elif b_pair in six:
                    decimal_places = 6
                elif b_pair in seven:
                    decimal_places = 7
                elif b_pair in eight:
                    decimal_places = 8

                if coin1 in zero:
                    coin_dec_place = 0
                elif coin1 in two:
                    coin_dec_place = 2

                # Check to see if pair is traded on other exchange
                if b_pair in self.binance_pairs:
                    if (int(time.time()) > data_update_interval) and (self._data_refresh_interval != 'OFF') and b_pair in self.binance_pairs:
                        try:
                            df = load_dataframe(str(b_pair), '6 days ago') # get 5 minute timeframe
                            df = standard_deviation(df, 'Close', 12) #1 hour standard deviation
                            df = MA(df, '12 Period Std Dev', 1440)
                            df = ratio(df, '12 Period Std Dev', '12 Period Std Dev 1440 MA') # ratio

                            stats_df.at[index, 'Volatility'] = float(df['12 Period Std Dev/12 Period Std Dev 1440 MA Ratio'].iloc[-1])

                            bid, ask = coin_quote(b_pair)
                            spread_multiplier = max(1, float(stats_df.at[index, 'Volatility']))
                            spread_1 = spread_1 * spread_multiplier

                            bid_price = round(bid * (1 - spread_1), decimal_places)
                            offer_price = round(ask * (1 + spread_1), decimal_places)

                            source = 'B'

                        except:
                            # cancel orders
                            source = 'PROOF'
                    else:
                        try:
                            bid, ask = coin_quote(b_pair)
                            spread_multiplier = max(1, float(stats_df.at[index, 'Volatility']))
                            bid_price = round(bid * (1 - spread_1), decimal_places)
                            offer_price = round(ask * (1 + spread_1), decimal_places)
                            source = 'B'
                            print(str(stats_df.at[index, 'Volatility']))

                        except:
                            source = 'PROOF'

                else:
                    source = 'PROOF'

                if source == 'PROOF':

                    # Get data from Proof exchange
                    pass

                # Check orders for fills and update


                #stats_df, tokens_df = check_orders(stats_df, tokens_df)

                # Put in orders

                if bid_price != 'OFF':
                    # Randomizes the order size between 90-110% so it does not look so bot-like.
                    size_bid = float(randint(self._position_size1 * 90, self._position_size1 * 110)/100)
                    qty_bid = round(size_bid/bid_price, coin_dec_place)

                    # Get balance on proof
                    #buy_coin_bal = get_balances(str(coin2)) # fix function
                    buy_coin_bal = 10000

                    # PLACE BID
                    if buy_coin_bal >= (qty_bid * bid_price):
                        try:
                            # Enter order
                            #bid_Id = place_limit_order(row['Pair'], 'BUY', qty_bid, bid_price) # not working yet
                            message = 'Bot1: Bid placed for ' + str(qty_bid) + ' ' + str(row['Pair']) + ' @ ' + str(bid_price)
                            print(message)
                            #stats_df.at[index, 'Bid_OrderID'] = bid_Id

                        except:
                            message = 'Bot1: Problem putting in bid for ' + str(qty_bid) + ' ' + str(row['Pair']) + ' @ ' + str(bid_price)
                            print(message)
                            # Optional: message yourself if error

                        # SLOW BOT
                        if (self._quote_refresh_interval2 != 'OFF') and (int(time.time()) > bot_slow):
                            #buy_coin_bal = get_balances(str(coin2))
                            size_bid2 = float(randint(self._position_size2 * 85, self._position_size2 * 115)/100)

                            spread_2 = spread_1 * self.spread_2
                            bid_price2 = round(bid * (1 - spread_2), decimal_places)
                            qty_bid2 = round(size_bid2/bid_price2, coin_dec_place)

                            if buy_coin_bal >= (qty_bid2 * bid_price2):
                                try:
                                    # Enter order 2
                                    #bid_Id2 = place_limit_order(row['Pair'], 'BUY', qty_bid2, bid_price2)
                                    message = 'Bot2: Bid placed for ' + str(qty_bid2) + ' ' + str(row['Pair']) + ' @ ' + str(bid_price2)
                                    print(message)
                                    #stats_df.at[index, 'Bid_OrderID2'] = bid_Id2
                                except:
                                    message = 'Bot2: Problem putting in bid for ' + str(qty_bid2) + ' ' + str(row['Pair']) + ' @ ' + str(bid_price2)
                                    print(message)
                                    # Optional: message yourself if error

                    else:
                        print(str(row['Pair']) + ' - Insufficient balance to place bid')


                if offer_price != 'OFF':
                    size_ask = float(randint(self._position_size1 * 85, self._position_size1 * 115)/100)
                    qty_ask = round(size_ask/offer_price, coin_dec_place)

                    sell_coin_bal = 100000 #get_balances(str(coin1)) # fix function

                    # PLACE OFFER
                    if sell_coin_bal >= (qty_ask * offer_price):
                        try:
                            # Enter order
                            #sell_Id = place_limit_order(row['Pair'], 'SELL', qty_ask, offer_price) # not working yet
                            message = 'Bot1: Offer placed for ' + str(qty_ask) + ' ' + str(row['Pair']) + ' @ ' + str(offer_price)
                            print(message)
                            #stats_df.at[index, 'Offer_OrderID'] = sell_Id

                        except:
                            message = 'Bot1: Problem putting in sell for ' + str(qty_ask) + ' ' + str(row['Pair']) + ' @ ' + str(offer_price)
                            print(message)
                            # Optional: message yourself if error

                        # SLOW BOT
                        if (self._quote_refresh_interval2 != 'OFF') and (int(time.time()) > bot_slow):
                            #sell_coin_bal = get_balances(str(coin1))
                            size_ask2 = float(randint(self._position_size2 * 85, self._position_size2 * 115)/100)

                            spread_2 = spread_1 * self.spread_2
                            ask_price2 = round(ask * (1 + spread_2), decimal_places)
                            qty_ask2 = round(size_ask2/ask_price2, coin_dec_place)

                            if sell_coin_bal >= (qty_ask2 * ask_price2):
                                try:
                                    # Enter order 2
                                    #ask_Id2 = place_limit_order(row['Pair'], 'BUY', qty_ask2, ask_price2)
                                    message = 'Bot2: Offer placed for ' + str(qty_ask2) + ' ' + str(row['Pair']) + ' @ ' + str(ask_price2)
                                    print(message)
                                    #stats_df.at[index, 'Offer_OrderID2'] = ask_Id2
                                except:
                                    message = 'Bot2: Problem putting in sell for ' + str(qty_ask2) + ' ' + str(row['Pair']) + ' @ ' + str(ask_price2)
                                    print(message)
                                    # Optional: message yourself if error

                    else:
                        print(str(row['Pair']) + ' - Insufficient balance to place sell')



            # Save stats to file
            try:
                stats_df.to_csv(stats_file, index=False)
                tokens_df.to_csv(tokens_file, index=False)
            except:
                pass


            # Rest time until it rotates again
            time.sleep(self._quote_refresh_interval)
            print()

            current_time = int(time.time())

            if current_time > bot_slow:
                bot_slow = current_time + self._quote_refresh_interval2

            if current_time > data_update_interval:
                data_update_interval = current_time + self._data_refresh_interval




