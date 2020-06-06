import logging

import azure.functions as func
from github import Github
import random
import string
import requests
import time

f = open("shorten/git_token.txt", "r")
token = str(f.read())
g = Github(token)
repo = g.get_repo("dattadebrup/link")
headers = {"Access-Control-Allow-Origin": "*"}

def get_random_alphaNumeric_string(stringLength=5):
    lettersAndDigits = string.ascii_letters + string.digits
    return ''.join((random.choice(lettersAndDigits) for i in range(stringLength)))

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    
    url = req.params.get('url')
    if not url:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            url = req_body.get('url')

    if url:
        ran_string= get_random_alphaNumeric_string()
        #content = '<head> <meta http-equiv="refresh" content="0; URL='+url+'" /> </head> <body> <p>If you are not redirected, <a href="'+url+'">click here</a>.</p> </body>'
        content = url 
        repo.create_file("/sites/"+ran_string + ".txt" , "New link added", content, branch="master")

        myobj = {'url': 'https://dattadebrup.github.io/Link_Shortener/shorten.html?li=' + ran_string}
        short_link = "https://git.io/" + requests.post('https://git.io/create', data = myobj).text 
        #time.sleep(0)
        return func.HttpResponse(short_link, headers = headers)
    else:
        return func.HttpResponse(
             "Please pass a url on the query string or in the request body",
             status_code=400, headers = headers
        )
