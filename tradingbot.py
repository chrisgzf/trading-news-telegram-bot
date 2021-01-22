import tweepy
import re
import time
import requests
import config

poll_delay = 15

twitter_consumer_key = config.twitter_consumer_key
twitter_consumer_secret = config.twitter_consumer_secret
twitter_access_token = config.twitter_access_token
twitter_access_token_secret = config.twitter_access_token_secret
twitter_subscribed_list_id = config.twitter_subscribed_list_id

telegram_token = config.telegram_token
telegram_group_id = config.telegram_group_id


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


while True:
    poll_list()
    time.sleep(poll_delay)
