from friendships.services import FriendshipService
from newsfeeds.models import NewsFeed


class NewsFeedService(object):

    @classmethod
    def fan_out_to_followers(cls, honk):
        newsfeeds = [
            NewsFeed(user=follower, honk=honk)
            for follower in FriendshipService.get_followers(honk.user)
        ]
        newsfeeds.append(NewsFeed(user=honk.user, honk=honk))
        NewsFeed.objects.bulk_create(newsfeeds)
