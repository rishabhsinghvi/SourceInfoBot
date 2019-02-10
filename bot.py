
'''
Due to the fact that one news source can have multiple domains/website, 'url' field in
the JSON file is an array of strings (even if only one domain is available)
News sources may also have multiple TLDs. 
'''
import praw
from tld import get_tld
from tld.utils import update_tld_names
import json
import sys
import time
from enum import Enum

data = None # data is global var so that it only fetches the info from json once.

class ErrType(Enum):
    error = "Error"
    info = "Info"
    debug = "Debug"


# Gets the domain name from the provided url using the tld package
def clean_url(url):
    res = get_tld(url, as_object=True)
    return res.domain 

# Populate the global variable data with the info in the json file. 
# TODO: use a database instead of JSON
def get_info():
    global data
    FILE = "data.json"
    data = json.loads(open(FILE,encoding="utf8").read())

# Gets the JSON object, by comparing the strings in the url array
# Returns None if no such object present
def find_info(_domain):
   # found_flag = False
    for object in data:
        for domain in object['url']:
            if domain == _domain:
                return object
    return None

# Processes the submission. Finds the JSON object using the domain name.
# If no such object found, logs the URL into the unknown.log file
# If found, creates a comment and returns it 
def proc_submission(submission):
    domain = clean_url(submission.url)
    object = find_info(domain)
    if object == None:
        log_unknown_url(submission.url)
        return None
    return create_comment(object)

# Creates the comments, using Reddit Style formatting
def create_comment(object):
    name = object['name']
    founded = object['founded']
    country = object['current_country']
    owner = object['current_owner']
    des = object['description']
    wiki = object['wiki']
    web = object['website']
    twitter = object['twitter']

    comment = """**Name: ** {}

 **Founded: ** {}

**Country: ** {}

**Owner: ** {}
            
**Info: ** {}
                
**More: ** [Wiki]({})| [Website]({}) | [Twitter]({})

""".format(name, founded, country, owner, des, wiki, web, twitter)

    return comment


def log(errtype, string):
    _time = time.ctime(time.time())
    log_string = _time + " : " + errtype.value + " - " + string+"\n" 
    with open("sourceinfo.log", "a+", encoding="utf8") as file:
        file.write(log_string)


def log_unknown_url(url):
    with open("unknown.log", "a+", encoding="utf8") as file:
        file.write(url+"\n")


def main():
    # Setup
    update_tld_names() #Forces the script to sync the tld names with the latest version from Mozilla
    get_info() # Populate 'data' with objects
    

    subreddits = ['worldnews', 'news']
    #threads = [] // Praw is not thread-safe

    reddit = praw.Reddit('SourceInfoBot', user_agent='SourceInfoBot v1.0')
    
    if reddit == None:
        log(ErrType.error, "Unable to connect to Reddit.")
        sys.exit()
    else:
        log(ErrType.info, "Connected to Reddit.")
        print("Connected to Reddit.")

    subs = "+".join(subreddits)

    for submission in reddit.subreddit(subs).stream.submissions():
        comment = proc_submission(submission)
        if comment == None:
            pass
        else:
            submission.reply(comment)


if __name__ == '__main__':
    main()
