import tweepy
import re
import time
import requests
import os
import yfinance as yf

from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext

try:
    import config
except ImportError:
    print("No config file found.")

poll_delay = 30

twitter_consumer_key = os.environ.get("TWITTER_CONSUMER_KEY") or config.twitter_consumer_key
twitter_consumer_secret = os.environ.get("TWITTER_CONSUMER_SECRET") or config.twitter_consumer_secret
twitter_access_token = os.environ.get("TWITTER_ACCESS_TOKEN") or config.twitter_access_token
twitter_access_token_secret = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET") or config.twitter_access_token_secret
twitter_subscribed_list_id = os.environ.get("TWITTER_SUBSCRIBED_LIST_ID") or config.twitter_subscribed_list_id

telegram_token = os.environ.get("TELEGRAM_TOKEN") or config.telegram_token
telegram_group_id = os.environ.get("TELEGRAM_GROUP_ID") or config.telegram_group_id


def search(update: Update, context: CallbackContext) -> None:
    ticker = context.args[0]
    t = yf.Ticker(ticker.upper())
    info = t.info
    reply = f"""**[{info["longName"]}](https://finance.yahoo.com/quote/{ticker})**
**Day Low/High:** {info["dayLow"]} {info["dayHigh"]}
**Bid/Ask:** {info["bid"]} {info["ask"]}"""

    update.message.reply_text(
        reply, disable_web_page_preview=True, parse_mode=ParseMode.MARKDOWN_V2)


def send_tweet_to_telegram(tweet):
    def escape_chars(x):
        to_escape = r'_*[]()~`>#+-=|{}.!'
        return re.sub(f'([{re.escape(to_escape)}])', r'\\\1', x)

    telegram_endpoint = f"https://api.telegram.org/bot{telegram_token}/sendMessage"

    username = escape_chars(tweet.user.screen_name)
    permalink = escape_chars(
        f"https://twitter.com/{username}/status/{tweet.id}")
    body = escape_chars(tweet.text)

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
    fin_list = api.list_timeline(
        list_id=twitter_subscribed_list_id, since_id=last_tweet_id)
    if fin_list:
        for tweet in reversed(fin_list):
            send_tweet_to_telegram(tweet)
        last_tweet_id = fin_list[0].id


updater = Updater(telegram_token)
updater.dispatcher.add_handler(CommandHandler('s', search))
updater.start_polling()

while True:
    poll_list()
    time.sleep(poll_delay)
