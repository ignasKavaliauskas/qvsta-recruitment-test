from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.cache import cache
from requests.exceptions import ConnectionError, HTTPError

import requests
import re
import bs4
import json


def indexView(request): 
    return render(request, 'index.html')

def analyseUrlView(request):
    targetUrl = request.POST['textUrl']

    # caching
    cacheKey = targetUrl
    cacheTime = 86400 #seconds = 24h
    cacheData = cache.get(cacheKey)

    # load scrapped results if available
    if cacheData:
        result = json.loads(cacheData)
        return render(request, 'analyseUrl.html', result)
    else:
        result = dict()

    # check URL
    try:
        r = requests.get(targetUrl)
        r.raise_for_status()

        # it may happen that the url changes from http://.. -> https://..
        targetUrl = r.url
        result['targetUrl'] = targetUrl

    except requests.exceptions.ConnectionError as err:
        result['error'] = 'Failed to establish a connection to {0}'.format(targetUrl)
        return render(request, 'index.html', result)

    except requests.exceptions.HTTPError as err:
        result['error'] = err
        return render(request, 'index.html', result)
    
    except Exception as err:
        result['error'] = err
        return render(request, 'index.html', result)

    # URL is ok. Let's get the required information
    try: # HTML version
        result['version'] = re.search(r'<!doctype .*?>', r.text, re.IGNORECASE).group()
    except:
        result['version'] = 'Version not found.'
    
    try: # Title
        rawMatch = re.search(r'<title>.*?</title>', r.text, re.IGNORECASE).group()
        result['title'] = bs4.BeautifulSoup(rawMatch, 'html.parser').string
    except:
        result['title'] = 'Title not found.'

    # How many headings of what level are in the document?
    result['headings'] = dict()
    for headLevel in range(1, 6): # possible head levels: h1,h2,..,h6
        searchResult = len(re.findall(r'<h{0}'.format(headLevel), r.text, re.IGNORECASE|re.MULTILINE))
        if(searchResult > 0):
            result['headings']['h{0}'.format(headLevel)] = searchResult
    
    ## old solution ##
        # How many internal and external links are in the document? 
        # re_pattern = r'((http|https):\/\/(?!{0})[\w\.\/\-=?#]+)'.format(targetUrl.split('//')[1])
        # externalLinks = re.findall(re_pattern, r.text, re.IGNORECASE|re.MULTILINE)
        # result['numOfExternalLinks'] = len(externalLinks)

        # re_pattern = r'(.*{0}.*)|(^\/.*$)'.format(targetUrl.replace('.', '\.'))
        # internalLinks = re.findall(re_pattern, r.text, re.IGNORECASE|re.MULTILINE)
        # result['numOfInternalLinks'] = len(internalLinks)
    ## end old solution ##

    # find all links on the page
    result['numOfInternalLinks'] = 0
    result['numOfExternalLinks'] = 0
    domainName = targetUrl.split('//')[-1].split('.')[1]

    # find ALL links in the document
    allLinks = re.findall(r'"((http|ftp|https)s?://.*?)"', r.text, re.IGNORECASE|re.MULTILINE)

    # check if they are internal or external links and count them
    for link in allLinks:
        if domainName.lower() in link[0].lower():
            result['numOfInternalLinks'] += 1
        else:
            result['numOfExternalLinks'] += 1


    # Are there any inaccessible links and how many?
    inaccessibleLinks = list()
    for link in allLinks:
        # just ask for the header in order to save time
        statusCode = requests.head(link[0]).status_code
        if statusCode >= 400 and statusCode <= 450:
            inaccessibleLinks.append(link[0])
    
    result['inaccessibleLinks'] = len(inaccessibleLinks)

    # Did the page contain a login-form? 
    rawMatch = re.findall(r'<form\b[^>]*>(.*?)<\/form>', r.text, re.IGNORECASE|re.MULTILINE|re.S)
    loginFormKeyWords = [r'login', r'sign in', r'sign-in', r'username', r'password']
    isLoginForm = False
    for match in rawMatch:
        for keyWord in loginFormKeyWords:
            if keyWord in match.lower():
                isLoginForm = True
                break
    
    if isLoginForm:
        result['containsLoginForm'] = 'Yes.'
    else:
        result['containsLoginForm'] = 'No form found.'
    
    # cache the results
    if not cacheData:
        cache.set(cacheKey, json.dumps(result), cacheTime)

    return render(request, 'analyseUrl.html', result)