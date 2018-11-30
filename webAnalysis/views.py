from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.cache import cache
from requests.exceptions import ConnectionError, HTTPError

from .webAnalyse import WebAnalyse
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
    else:
        result = WebAnalyse(targetUrl).analyse()
        cache.set(cacheKey, json.dumps(result), cacheTime)

    return render(request, 'analyseUrl.html', result)