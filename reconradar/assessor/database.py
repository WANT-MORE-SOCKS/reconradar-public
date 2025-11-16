from django.db import models
from time import time
from json import loads
import io

expiration_time = loads(io.open("config.json").read())["expiration_time_seconds"]

class Response(models.Model):
    query = models.TextField()
    content = models.TextField()
    epoch = models.BigIntegerField()

    def to_content(self):
        return self.content

def fetch_cache(query):
    """
    returns either a Response (Django Model) if a fresh entry is found
    or False if an entry has gone stale or none is found.
    """
    try:
        responses = Response.objects.filter(query=query)
        response = responses[0]
        print("Cache hit!")
        if (response.epoch < (time() - expiration_time)):
            print("Entry has gone stale. Deleting...")
            response.delete()
            return False
        print(response)
        return response
    except Response.DoesNotExist:
        return False
    except IndexError:
        return False

def cache_response(query, content):
    new_response = Response()
    new_response.query = query
    new_response.content = content
    new_response.epoch = int(time())
    
    new_response.save()
    print("saved new response")
