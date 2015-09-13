import requests
import xml.etree.ElementTree as ET

__author__ = 'adames'


class IndeedApi():

    BROWSER = 'Mozilla/%2F4.0%28Firefox%29'
    API_VERSION = 2

    def __init__(self, token, channel, user_ip):
        # api params
        self.__url_base = 'http://api.indeed.com/ads/apisearch'
        self.__publisher = token
        self.__channel = channel
        self.__user_ip = user_ip
        self.__user_agent = self.BROWSER
        self.__api_version = self.API_VERSION

        # request params
        self.query = None
        self.job_time = None
        self.posts_since = 15

        self.city = None
        self.country = None

        self.filter = 1
        self.sort = 'date'

        self.index_start = 0
        self.index_limit = 100

    def search_for(self, keywords, job_time='fulltime', posts_since=15):
        jt = ['fulltime', 'parttime', 'internship']

        if type(keywords) is list:
            s = ', '.join(keywords)
        elif type(keywords) in (str, unicode):
            s = keywords
        else:
            exit('The keywords need to be passed as a list of strings or a single string delimited by comas.')

        if job_time not in jt:
            exit('Job time can only be one of the following:', jt)

        if type(posts_since) is not int:
            exit('The number of days needs to be integer.')

        self.query = s
        self.job_time = job_time
        self.posts_since = posts_since

    def set_location(self, city, country):
        if type(city) not in (str, unicode):
            exit('City parameter needs to be string of characters.')

        if type(country) not in (str, unicode) or len(country) != 2:
            exit('Country parameter needs to be the 2 characters ISO code (ex. "de").')

        self.city = city
        self.country = country.lower()

    def set_filters(self, filter=1, posts_since=15, sort='date'):
        if type(filter) is not int:
            exit('Filter needs to be integer.')

        if type(sort) not in (str, unicode):
            exit('Sort by needs to be a string of characters.')

        self.filter = filter
        self.sort = sort

    def get_jobs(self, params_dict=None, index_start=0, index_limit=100):
        if type(index_start) is not int or type(index_limit) is not int:
            exit('The indexes need to be integers.')

        self.index_start = index_start
        self.index_limit = index_limit

        if params_dict is not None and type(params_dict) is dict:
            params = params_dict.copy()
        else:
            params = dict(
                publisher=self.__publisher,
                q=self.query,
                l=self.city,
                jt=self.job_time,
                start=self.index_start,
                limit=self.index_limit,
                sort=self.sort,
                fromage=self.posts_since,
                filter=self.filter,
                co=self.country,
                chnl=self.__channel,
                userip=self.__user_ip,
                useragent=self.__user_agent,
                v=self.__api_version
            )

        for item in self.__request(self.__url_base, params):
            yield item

    @staticmethod
    def __request(url_base, params):
        try:
            r = requests.get(url_base, params=params)
        except Exception as e:
            exit('Error while sending request to Indeed API:\n', e)

        # print 'Request status:', r.status
        print 'URL:', r.url

        s = r.content

        root = ET.fromstring(s)

        for results in root.iter('results'):
            for result in results:
                d = {}
                for field in result:
                    d[field.tag] = field.text
                yield d