import pickle
from datetime import datetime

import redis
import tweepy

# Get your credentials from https://developer.twitter.com/en/portal/projects-and-apps
api_key = ""
api_key_secret = ""

access_token = ""
access_token_secret = ""

bearer_token = ""

redis_pass = ''

# variables
r = redis.Redis(host='localhost', port=6379, db=1, password=redis_pass)

client = tweepy.Client(bearer_token, api_key, api_key_secret, access_token, access_token_secret)

auth = tweepy.OAuth1UserHandler(api_key, api_key_secret, access_token, access_token_secret)
api = tweepy.API(auth)

search_terms = ["한복"]


def submit_tweet(tweet):
    global r
    key = datetime.now().strftime("%Y%m%d_%H%M%S.%f")
    r.set(key, pickle.dumps(tweet))
    print(f"Saved tweet to database (key: {key})")


class MyStream(tweepy.StreamingClient):
    def on_connect(self):
        print("Connected")

    def on_tweet(self, tweet):
        submit_tweet(tweet.text)

    def on_disconnect(self):
        print("Disconnected")
        stream.disconnect()

    def on_on_limit(self, notice):
        print("Limit notice:", notice)


stream = MyStream(bearer_token=bearer_token)

# rules = stream.get_rules()
# print(rules)

# for i in range(len(rules)):
#     print(rules[0][i].id)
#     stream.delete_rules(rules[0][i].id)

# for term in search_terms:
#     stream.add_rules(tweepy.StreamRule(term))

# Starting stream
stream.filter(tweet_fields=["referenced_tweets"])
