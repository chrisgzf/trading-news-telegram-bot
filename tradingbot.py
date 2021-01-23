import tweepy
import re
import time
import requests
import os
import numpy as np
import yfinance as yf
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import io

from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext
from telegram.utils.helpers import escape_markdown

try:
    import config
except ImportError:
    print("No config file found.")

poll_delay = 30

twitter_consumer_key = os.environ.get(
    "TWITTER_CONSUMER_KEY") or config.twitter_consumer_key
twitter_consumer_secret = os.environ.get(
    "TWITTER_CONSUMER_SECRET") or config.twitter_consumer_secret
twitter_access_token = os.environ.get(
    "TWITTER_ACCESS_TOKEN") or config.twitter_access_token
twitter_access_token_secret = os.environ.get(
    "TWITTER_ACCESS_TOKEN_SECRET") or config.twitter_access_token_secret
twitter_subscribed_list_id = os.environ.get(
    "TWITTER_SUBSCRIBED_LIST_ID") or config.twitter_subscribed_list_id

telegram_token = os.environ.get("TELEGRAM_TOKEN") or config.telegram_token
telegram_group_id = os.environ.get(
    "TELEGRAM_GROUP_ID") or config.telegram_group_id

matplotlib.use('agg')

def send_graph_using_ticker(update: Update,
                            context: CallbackContext,
                            t,
                            graph_period: str,
                            ticker: str,
                            interval: str = "1m",
                            prepost: bool = False):
    history = t.history(period=graph_period,
                        interval=interval,
                        prepost=prepost)
    last_data = history.tail(1)
    last_data_time = last_data.index.strftime("%H:%M:%S")[0]
    last_data_price = round(last_data["Open"][0], 2)
    title = f"{ticker.upper()} ({last_data_price} at {last_data_time})"

    dt = history["Open"].index
    N = len(dt)
    ind = np.arange(N)

    def format_date(x, pos=None):
        thisind = np.clip(int(x+0.5), 0, N-1)
        return dt[thisind].strftime('%Y-%m-%d')

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(ind, history["Open"].values, "-")
    ax.xaxis.set_major_formatter(FuncFormatter(format_date))
    ax.set_title(title)
    ax.set_ylabel("Price ($)")
    ax.set_xlabel("Date/Time")
    fig.autofmt_xdate()
    img = io.BytesIO()
    fig.savefig(img, format="png")
    img.seek(0)
    fig.clf()

    context.bot.send_photo(chat_id=update.effective_chat.id,
                           photo=img)


def s(update: Update, context: CallbackContext):
    search(update, context, True)


def ss(update: Update, context: CallbackContext):
    search(update, context, False)


def search(update: Update, context: CallbackContext, send_graph: bool) -> None:
    ticker = context.args[0]
    t = yf.Ticker(ticker.upper())
    info = t.info
    reply = f"""[*{escape_markdown(info["longName"], version=2)} \({escape_markdown(ticker.upper(), version=2)}\)*]({escape_markdown(f"https://finance.yahoo.com/quote/{ticker}", version=2, entity_type="TEXT_LINKS")})
Day Low/High: {escape_markdown(str(info["dayLow"]), version=2)} {escape_markdown(str(info["dayHigh"]), version=2)}
Bid/Ask: {escape_markdown(str(info["bid"]), version=2)} {escape_markdown(str(info["ask"]), version=2)}"""

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=reply,
                             disable_web_page_preview=True,
                             parse_mode=ParseMode.MARKDOWN_V2)

    if send_graph:
        send_graph_using_ticker(update, context, t, "1d", ticker)


def chart(graph_period: str, interval: str, prepost: bool):
    return lambda u, c: send_chart(u, c, graph_period, interval, prepost)


def send_chart(update: Update, context: CallbackContext, graph_period: str,
               interval: str, prepost: bool) -> None:
    ticker = context.args[0]
    t = yf.Ticker(ticker.upper())
    send_graph_using_ticker(update, context, t, graph_period, ticker, interval,
                            prepost)


def send_tweet_to_telegram(tweet):
    telegram_endpoint = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
    username = escape_markdown(tweet.user.screen_name, version=2)
    permalink = escape_markdown(
        f"https://twitter.com/{username}/status/{tweet.id}",
        version=2,
        entity_type="TEXT_LINKS")
    body = escape_markdown(tweet.text, version=2)

    message = f"""
[New tweet]({permalink}) from *[@{username}](https://twitter.com/{username})*:
{body}
    """
    print(message)

    data = {
        "chat_id": telegram_group_id,
        "text": message,
        "parse_mode": "MarkdownV2",
        "disable_web_page_preview": True,
    }
    req = requests.post(telegram_endpoint, data=data)
    print(req.content)


# Set up tweepy
auth = tweepy.OAuthHandler(twitter_consumer_key, twitter_consumer_secret)
auth.set_access_token(twitter_access_token, twitter_access_token_secret)
api = tweepy.API(auth)

# Set up last tweet
fin_list = api.list_timeline(list_id=twitter_subscribed_list_id)
last_tweet_id = fin_list[0].id


def poll_list():
    global last_tweet_id
    fin_list = api.list_timeline(list_id=twitter_subscribed_list_id,
                                 since_id=last_tweet_id)
    if fin_list:
        for tweet in reversed(fin_list):
            send_tweet_to_telegram(tweet)
        last_tweet_id = fin_list[0].id


updater = Updater(telegram_token)
updater.dispatcher.add_handler(CommandHandler('s', s))
updater.dispatcher.add_handler(CommandHandler('ss', ss))
updater.dispatcher.add_handler(CommandHandler('1d', chart("1d", "1m", False)))
updater.dispatcher.add_handler(CommandHandler('3d', chart("3d", "2m", True)))
updater.dispatcher.add_handler(CommandHandler('5d', chart("5d", "5m", True)))
updater.start_polling()

print("Setup complete. Polling.")

while True:
    poll_list()
    time.sleep(poll_delay)
