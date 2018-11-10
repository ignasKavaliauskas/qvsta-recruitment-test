from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from requests.exceptions import ConnectionError
import requests
import re
import bs4

def indexView(request):
    return render(request, 'index.html')

def analyseUrlView(request):
    result = dict()

    targetUrl = request.POST['textUrl']

    if not 'http://' in targetUrl and not 'https://' in targetUrl:
        targetUrl = 'http://' + targetUrl

    # is it a valid url?
    try:
        r = requests.get(targetUrl)
        targetUrl = r.url
        # print(r.text)
    except Exception as e:
        # if not, redirect back to the home page
        # display this message
        result['error'] = "Invalid or unreachable URL"

        return render(request, 'index.html', result)
    
    result['targetUrl'] = targetUrl

    # grab html version of the document
    try:
        result['version'] = re.search(r'<!doctype .*?>', r.text, re.IGNORECASE).group()
    except:
        result['version'] = 'Version not found.'
    
    # page title
    try:
        raw_match = re.search(r'<title>.*?</title>', r.text, re.IGNORECASE).group()
        result['title'] = bs4.BeautifulSoup(raw_match, 'html.parser').string
    except:
        result['title'] = 'Title not found.'

    # How many headings of what level are in the document?
    result['headings'] = dict()
    for headLevel in range(1, 6): # possible head level: h1,h2,..,h6
        searchResult = len(re.findall(r'<h{0}'.format(headLevel), r.text, re.IGNORECASE|re.MULTILINE))
        if(searchResult > 0):
            result['headings']['h{0}'.format(headLevel)] = searchResult
    
    # How many internal and external links are in the document? 
    re_pattern = r'((http|https):\/\/(?!{0})[\w\.\/\-=?#]+)'.format(targetUrl.split('//')[1])
    result['numOfExternalLinks'] = len(re.findall(re_pattern, r.text, re.IGNORECASE|re.MULTILINE))

    re_pattern = r'(.*{0}.*)|(^\/.*$)'.format(targetUrl.replace('.', '\.'))
    result['numOfInternalLinks'] = len(re.findall(re_pattern, r.text, re.IGNORECASE|re.MULTILINE))

    # Are there any inaccessible links and how many?

    # Did the page contain a login-form? 
    # Right now just checking if there is ANY form , TODO: check if the form is used for login
    try:
        result['containsLoginForm'] = re.search(r'<form.*>', r.text, re.IGNORECASE|re.MULTILINE) != None
    except:
        result['containsLoginForm'] = 'No form found.'

    return render(request, 'analyseUrl.html', result)