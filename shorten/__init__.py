import logging

import azure.functions as func
from github import Github
import random
import string
import requests
import time
import os 
import re

#f = open("shorten/git_token.txt", "r")
#token = str(f.read())
git_token = os.environ["token"]
g = Github(git_token)
repo = g.get_repo("dattadebrup/link")
headers = {"Access-Control-Allow-Origin": "*"}
server_token = os.environ["recaptcha_token"]

def get_random_alphaNumeric_string(stringLength=5):
    lettersAndDigits = string.ascii_letters + string.digits
    return ''.join((random.choice(lettersAndDigits) for i in range(stringLength)))

def is_url(url):
    if ((url[0:3] != 'htt') and (url[0:3] !='ftp')) :
        url = 'http://' + url

    regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return (re.match(regex, url))

def is_valid_token(site_token):

    obj_recaptcha = {'secret': server_token,'response' : site_token}
    resp = requests.post('https://www.google.com/recaptcha/api/siteverify', data = obj_recaptcha)
    data = resp.json()
    logging.info(data["success"])
    return (data["success"])

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    
    url = req.params.get('url')
    site_token = req.params.get('token')
    is_url_current = is_url(url)
    is_valid_token_current = is_valid_token(site_token)

    if is_url_current and is_valid_token_current:
        ran_string= get_random_alphaNumeric_string()
        #content = '<head> <meta http-equiv="refresh" content="0; URL='+url+'" /> </head> <body> <p>If you are not redirected, <a href="'+url+'">click here</a>.</p> </body>'
        content = url 
        repo.create_file("sites/"+ran_string + ".txt" , "New link added", content, branch="master")

        myobj = {'url': 'https://dattadebrup.github.io/Link_Shortener/shorten.html?li=' + ran_string}
        short_link = "https://git.io/" + requests.post('https://git.io/create', data = myobj).text 
        
        return func.HttpResponse(short_link, headers = headers)

    elif is_url_current and not is_valid_token_current:
        return func.HttpResponse("Recaptcha verification failed", headers = headers)

    elif not is_url_current and is_valid_token_current:
        return func.HttpResponse("Not a valid url", headers = headers)
    else:
        return func.HttpResponse(
             "Error",
             #status_code=400, 
             headers = headers
        )
