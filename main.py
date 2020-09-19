import re
import tweepy
from tweepy import OAuthHandler
import praw
from textblob import TextBlob
import api_keys
import matplotlib.pyplot as plt

class Twitter(object):
    '''
    Twitter Class for module. Get relevant API Keys from app.twitter and setup developer account.

    Polarity quantifies the sentiment of the queried news where:
    0 means Neutral Sentiment
    Greater than 0 means Positive Sentiment
    Less than 0 means Negative Sentiment
    '''
    polarity = []

    def __init__(self):
        # Access Keys and Secrets
        twitter_keys = api_keys.twitter_keys()
        consumer_Key = twitter_keys['consumer_key']
        consumer_Secret = twitter_keys['consumer_secret']
        access_Token = twitter_keys['access_token']
        access_Secret = twitter_keys['access_secret']

        # Attempt Authentication
        try:
            self.auth = OAuthHandler(consumer_Key,consumer_Secret)
            self.auth.set_access_token(access_Token,access_Secret)
            self.api = tweepy.API(self.auth)
        except:
            print('Error:Authentication Failed!')


    def clean_tweet(self, tweet):
        '''
        Used to clean tweet text by removing links, special characters
        using simple regex statements.
        '''
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

    def get_tweet_sentiment(self, tweet):
        '''
        Uses TextBlob (based on NLTK) to process the text and report a suitable polarity rating
        '''
        analysis = TextBlob(self.clean_tweet(tweet))
        polarity = analysis.sentiment.polarity

        self.polarity.append(round(polarity,5))

        if polarity > 0:
            return 'positive'
        elif polarity == 0:
            return 'neutral'
        else:
            return 'negative'

    def get_tweets(self, query, count = 10):
        '''
        Tweets are fetched and stored in tweets dictionary with text and sentiment keys
        '''
        tweets = []

        try:
            fetched_tweets = self.api.search(q = query, count = count)

            for tweet in fetched_tweets:

                parsed_tweet = {}
                parsed_tweet['text'] = tweet.text
                parsed_tweet['sentiment'] = self.get_tweet_sentiment(tweet.text)

                if tweet.retweet_count > 0: #If tweets have retweets it's added only once

                    if parsed_tweet not in tweets:
                        tweets.append(parsed_tweet)
                else:
                    tweets.append(parsed_tweet)

            return tweets

        except tweepy.TweepError as e:
            print('Error: '+str(e))

class Reddit(object):
    '''
       Reddit Class for module. Get relevant API Keys from app.twitter and setup developer account.

       Polarity quantifies the sentiment of the queried news where:
       0 means Neutral Sentiment
       Greater than 0 means Positive Sentiment
       Less than 0 means Negative Sentiment
    '''
    polarity = []

    def __init__(self):
        try:
            reddit_keys = api_keys.reddit_keys()
            self.reddit = praw.Reddit(client_id=reddit_keys['client_id'],
                                    client_secret=reddit_keys['client_secret'],
                                    user_agent='Teddddyyyy')
        except:
            print('Error: Authentication Error!')

    def get_post_sentiment(self,headline):
        '''
        Uses TextBlob (based on NLTK) to process the text and report a suitable polarity rating
        '''
        analysis = TextBlob(headline)
        polarity = analysis.sentiment.polarity

        self.polarity.append(round(polarity, 5))

        if polarity > 0:
            return 'positive'
        elif polarity == 0:
            return 'neutral'
        else:
            return 'negative'

    def get_headlines(self,query,limit):
        news = []
        try:
            posts = self.reddit.subreddit('all').search(query=query,sort='top',time_filter='month',limit=limit)
            for post in posts:
                parsed_posts = {}
                parsed_posts['text'] = post.title
                parsed_posts['sentiment'] = self.get_post_sentiment(post.title)

                if parsed_posts not in news:
                    news.append(parsed_posts)
            return news

        except:
            print('Error: Something went wrong!')

def main():
    '''
    Driver Code
    '''
    positive_senti = []
    negative_senti = []
    neutral_senti = []

    query = 'Enter Search String Here'
    api_twitter = Twitter()
    tweets = api_twitter.get_tweets(query=query, count=1000)

    positive_senti.extend([tweet for tweet in tweets if tweet['sentiment'] == 'positive'])
    negative_senti.extend([tweet for tweet in tweets if tweet['sentiment'] == 'negative'])
    neutral_senti.extend([tweet for tweet in tweets if tweet['sentiment'] == 'neutral'])

    api_reddit = Reddit()
    reddit = api_reddit.get_headlines(query=query,limit=None) #Limit Ranges from Default 25 to 1000, None means no limit

    positive_senti.extend([post for post in reddit if post['sentiment'] == 'positive'])
    negative_senti.extend([post for post in reddit if post['sentiment'] == 'negative'])
    neutral_senti.extend([post for post in reddit if post['sentiment'] == 'positive'])

    # Calculating Percentages
    total_items = len(tweets)+len(reddit)
    print(f'Relevant Reddit posts: {len(reddit)}')
    print(f'Relevant Tweets: {len(tweets)}')
    print(f'Positive Sentiments percentage: {(100 * len(positive_senti) / total_items):0.3f} %')
    print(f'Negative Sentiments percentage: {(100 * len(negative_senti) / total_items):0.3f} %')
    print(f'Neutral Sentiments percentage: {(100 * len(neutral_senti) / total_items):0.3f} %')


    #Plotting Pie Chart Using Matplotlib
    plt.axis("equal")
    pies = [len(positive_senti),len(neutral_senti),len(negative_senti)]
    labels = ['Positive','Neutral','Negative']
    plt.pie(pies,labels=labels,radius=1,explode=(0.1,0.0,0.1),shadow=True,startangle=90)
    plt.tight_layout()
    plt.title(f'Sentiment of {total_items} People on {query}')
    centre_circle = plt.Circle((0, 0), 0.70, fc='white')
    fig = plt.gcf()
    fig.gca().add_artist(centre_circle)
    plt.show()

    print('----------------------------------')
    print('\n------------------Positive Sentiments---------------------\n')
    for item in positive_senti[:10]:
        print(item['text'])

    print('\n-------------------Negative Sentiments---------------------\n')
    for item in negative_senti[:10]:
        print(item['text'])

    print('\n--------------------Neutral Sentiments---------------------\n')
    for item in neutral_senti[:10]:
        print(item['text'])

if __name__ == '__main__':
    main()


