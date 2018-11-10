from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from requests.exceptions import ConnectionError, HTTPError, InvalidURL, InvalidSchema, MissingSchema
import requests
import re
import bs4

def indexView(request):
    return render(request, 'index.html')

def analyseUrlView(request):
    result = dict()
    targetUrl = request.POST['textUrl']
    
    # check URL
    try:
        r = requests.get(targetUrl)
        r.raise_for_status()

        # it may happen that the url changes from http://.. -> https://..
        targetUrl = r.url
        result['targetUrl'] = targetUrl

    except requests.exceptions.ConnectionError as err:
        # raised when a 
        result['error'] = 'Failed to establish a connection to {0}'.format(targetUrl)
        return render(request, 'index.html', result)

    except requests.exceptions.HTTPError as err:
        result['error'] = err
        return render(request, 'index.html', result)
    
    except Exception as err:
        result['error'] = err
        return render(request, 'index.html', result)


    # grab html version of the document

    try:
        result['version'] = re.search(r'<!doctype .*?>', r.text, re.IGNORECASE).group()
    except:
        result['version'] = 'Version not found.'
    
    # page title
    try:
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
    
    # How many internal and external links are in the document? 
    # re_pattern = r'((http|https):\/\/(?!{0})[\w\.\/\-=?#]+)'.format(targetUrl.split('//')[1])
    # externalLinks = re.findall(re_pattern, r.text, re.IGNORECASE|re.MULTILINE)
    # result['numOfExternalLinks'] = len(externalLinks)

    # re_pattern = r'(.*{0}.*)|(^\/.*$)'.format(targetUrl.replace('.', '\.'))
    # internalLinks = re.findall(re_pattern, r.text, re.IGNORECASE|re.MULTILINE)
    # result['numOfInternalLinks'] = len(internalLinks)

    # find all links on the page
    result['numOfInternalLinks'] = 0
    result['numOfExternalLinks'] = 0
    domainName = targetUrl.split('//')[-1].split('.')[1]

    # check if they are internal or external links and count them
    allLinks = re.findall(r'"((http|ftp|https)s?://.*?)"', r.text, re.IGNORECASE|re.MULTILINE)
    for link in allLinks:
        if domainName.lower() in link[0].lower():
            result['numOfInternalLinks'] += 1
        else:
            result['numOfExternalLinks'] += 1


    # Are there any inaccessible links and how many?
    inaccessibleLinks = list()
    for link in allLinks:
        statusCode = requests.head(link[0]).status_code
        if statusCode >= 400 and statusCode <= 450:
            inaccessibleLinks.append(link[0])
    
    result['inaccessibleLinks'] = len(inaccessibleLinks)
    print(inaccessibleLinks)

    # Did the page contain a login-form? 
    # Right now just checking if there is ANY form , TODO: check if the form is used for login
    try:
        rawMatch = re.search(r'<form.*>.*<\/form>', r.text, re.IGNORECASE|re.MULTILINE)
        loginFormKeyWords = [r'.*login.*', r'.*sign.*in.*']
        for keyWord in loginFormKeyWords:
            if len(re.findall(r'{0}'.format(keyWord), rawMatch.group().lower(), re.IGNORECASE|re.MULTILINE)) > 0:
                result['containsLoginForm'] = True
                break
    except:
        result['containsLoginForm'] = 'No form found.'

    return render(request, 'analyseUrl.html', result)