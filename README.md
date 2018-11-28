# Proof Marketmaking

BOT README

How to run:

	python
	>>from market_maker import *
	>>b = Bot()
	>>b.start()

Press CTRL + C to kill.

Dont forget to add in binance api key to the b_data file first. Ask me if you dont have an account.

TO DO:

- Connect bot to proof API wrapper
- Add logic for making calculations within proof exchange
- Add 2nd source for pulling data
- Finish logic for arbitrage

Mission

- The primary goal of this bot is to establish a liquid market with minimal amount of risk to the operators. If executed correctly, it should create liquidity that will attract traders to the exchange, in turn creating more liquidity and attracting more traders.

- The secondary goal of this bot is to generate a profit for the operators, which would also be nice. 


@Operator

- There are 2 options for running the bot. The easiest and lowest risk way of accomplishing the above is to offload inventory at a different exchange, aka arbitrage. The only downside to this is it requires more capital since you will need balances in multiple accounts. The other alternative is to settle everything on the proof exchange. 
- To do arbitrage, you’ll need a (in this case Binance) account with sufficient balance. Sufficient would be roughly the equivalent size as the trading account on the proof exchange. 
- To turn off arbitrage, simply set the self.arbitrage setting in the __init__ of the bot file to ‘OFF’. With arbitrage ‘OFF’. This carries a little more risk and we won’t know how it will perform until we actually run it live.

Description:

- The bot consists of 2 levels of orders on each side of the market book (2 bids and 2 asks). The faster bot will bid/ask a tighter spread for a lower quantity. The slower bot will bid/ask a wider spread with a larger capital amount. The purpose of this is to offer bigger traders a better order book to interact with. 
- The slower bot can be turned off. 
- By default, the bot will gather quotes via Binance (can be changed), and offer it at a slightly wider spread on the proof exchange, offering an opportunity for arbitrage to offset inventory while keeping the spread relatively tight. 
- The quotes on the fast and slow bot are updated every 30 seconds and 10 min respectively.

- The bot will gather data every 5 minutes from Binance to get a sense of the market environment. In more volatile market (Faster moving) environments, the spread will be adjusted accordingly to mitigate risk. For example, instead of adding 0.2% to the ask, it will add 0.5% if the price is rising quickly, etc.

- The bot will create and save 2 files: a spreadsheet on the stats of all the pairs, and one on all the tokens. Looking at these will show the operator a snapshot of all activity in real time- such as total volume traded, inventory, profit, order IDs, commissions paid, volatility, and balances of each pair and token.  

Adjustable Settings:

- Fast bot quote refresh interval: Default 30 seconds
- Slow bot quote refresh interval: Default 10 minutes (can be turned OFF)
- Fast bot order size
- Slow bot order size
- Fast bot spread (premium it adds onto binance quotes)
- Arbitrage ON/OFF
- Interval at which it take market data to help with calculations: Default 5 min (can be turned OFF)
- Maximum position size (if arbitrage OFF)


