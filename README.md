# Stonks Bot

A Telegram bot that

- polls a trading-related [Twitter list](https://help.twitter.com/en/using-twitter/twitter-lists) of your choosing, and sends you or your Telegram group a message whenever there are new tweets
- provides commands that quickly fetches live market data, charts, and technical analysis data (soon!) from Yahoo Finance
- ... who knows? We are still rapidly building features that are useful to us!

This is a very recent hobby project that was very quickly built in a few hours to serve our trading discussion needs. As such, some features might be buggy, and code quality will slowly be worked on.

## Usage Disclaimer

We take zero responsibility if your use of this bot and/or source code provides you with inaccurate or buggy information for your own trades. In fact, we take no responsibility for anything at all.

## Source Code

Stonks bot has a few components

1. Twitter List Polling
1. Stock searching, charting, TA
1. Market opening and closing messages

Most of these are written in Python 3 or are just shell scripts run with cron.

To set-up the Python scripts:

1. Clone the repository
1. [Install `poetry`](https://python-poetry.org/docs/#installation)
1. Run `poetry install` to install all necessary dependencies
1. Copy `config.py.example` to `config.py`, and fill it up with the required Twitter API secrets and Telegram bot tokens. (Alternatively, you can export environment variables for the secrets. Stonks bot reads in secrets from environment variables too. This is extremely useful for deployments.)
1. Run `poetry run python tradingbot.py` to start the bot.

### Twitter List Polling

We make use of [`tweepy`](https://github.com/tweepy/tweepy) to access the [Twitter API](https://developer.twitter.com/en/docs). The bot polls the list set in `twitter_subscribed_list_id` once every `poll_delay` seconds, and sends a Telegram message containing the tweet info if there are new tweeets.

You can view the code for it in `tradingbot.py`.

### Stock searching, charting, TA

We make use of [`yfinance`](https://github.com/ranaroussi/yfinance) to access live Yahoo Finance data.

Charting is done using `pandas` and `matplotlib`.

### Market opening and closing messages

The bot can also be set up to send market opening and closing messages.

The messages are sent using `marketclose.sh` and `marketopen.sh` using a shell script, by calling cURL on the Telegram bot API.

To use `marketclose.sh` and `marketopen.sh`, add these to crontab

```
25 22 * * 1-5   /home/chris/marketopen.sh
0 5 * * 2-6     /home/chris/marketclose.sh
```

Take note that there is no timezone customization for this functionality at the moment, so the cron jobs above are both set to GMT+8 Singapore Time. You can customise them accordingly.

You will need to export your telegram bot token to `$TELEGRAM_TOKEN`.

## Contributing

Just submit a PR! 😇

## License

This project is open-source, and is licensed with the MIT license. See [our license](blob/master/LICENSE) for details.
