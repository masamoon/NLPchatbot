import praw
from random import randint



class reddit:

    def get_joke(self):
        r = praw.Reddit(user_agent='Test Script by /u/bboe')
        r.login('blackality', 'andrelopes')

        submissions = r.get_subreddit('jokes').get_top(limit=20)
        submissions = list(submissions)
        #return[submissions[0],submissions[0].selftext()]
        r = randint(0,19)
        return [submissions[r].title,submissions[r].selftext]

    def get_news(self):
        r = praw.Reddit(user_agent='Test Script by /u/bboe')
        r.login('blackality', 'andrelopes')

        submissions = r.get_subreddit('worldnews').get_top(limit=10)
        submissions = list(submissions)
        # return[submissions[0],submissions[0].selftext()]
        news = []
        for sub in submissions:
            news.append([sub.title,sub.url])

        return news

x = reddit()