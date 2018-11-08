from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from requests.exceptions import ConnectionError
import requests
import re
import bs4

def indexView(request):
    return render(request, 'index.html')

def analyseUrlView(request):
    targetUrl = request.POST['textUrl']

    if not 'http://' in targetUrl and not 'https://' in targetUrl:
        targetUrl = 'http://' + targetUrl

    # is it a valid url?
    try:
        r = requests.get(targetUrl)
        # print(r.text)
    except Exception as e:
        # if not, redirect back to the home page
        # display this message
        print("invalid/unreachable url", e)
        return HttpResponseRedirect('/index/')
    
    result = dict()
    result['targetUrl'] = targetUrl

    # grab html version of the document
    result['version'] = re.search(r'<!doctype .*?>', r.text, re.IGNORECASE).group()
    
    # page title
    raw_match = re.search(r'<title>.*?</title>', r.text, re.IGNORECASE).group()
    result['title'] = bs4.BeautifulSoup(raw_match, 'html.parser').string

    # How many headings of what level are in the document?
    result['headings'] = dict()
    for headLevel in range(1, 6):
        searchResult = len(re.findall(r'<h{0}'.format(headLevel), r.text, re.IGNORECASE|re.MULTILINE))
        if(searchResult > 0):
            result['headings']['h{0}'.format(headLevel)] = searchResult
    
    # How many internal and external links are in the document? 
    
    # Are there any inaccessible links and how many?
    # Did the page contain a login-form?
    return render(request, 'analyseUrl.html', result)