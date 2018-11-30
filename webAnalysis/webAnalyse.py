import requests
import re
import bs4

class WebAnalyse:

    def __init__(self, url):
        self.targetUrl = url
        self.result = dict()
        self.r = None
        self.allLinks = None
        self.domainName = None
    
    def analyse(self):
        if self.checkUrl():
            self.getHtmlVersion()
            self.getTitle()
            self.countHeadings()
            self.findAllLinks()
            self.groupLinks()
            self.getInaccessibleLinks()
            self.findLoginForm()

        return self.result

    
    def checkUrl(self):
        try:
            self.r = requests.get(self.targetUrl)
            self.r.raise_for_status()

            # it may happen that the url changes from http://.. -> https://..
            self.targetUrl = self.r.url
            self.result['targetUrl'] = self.targetUrl

            return True

        except requests.exceptions.ConnectionError as err:
            self.result['error'] = 'Failed to establish a connection to {0}'.format(self.targetUrl)
            return False

        except requests.exceptions.HTTPError as err:
            self.result['error'] = err
            return False
        
        except Exception as err:
            self.result['error'] = err
            return False
    
    def getHtmlVersion(self):
        try: # HTML version
            self.result['version'] = re.search(r'<!doctype .*?>', self.r.text, re.IGNORECASE).group()
        except:
            self.result['version'] = 'Version not found.'
    
    def getTitle(self):
        try: # Title
            rawMatch = re.search(r'<title>.*?</title>', self.r.text, re.IGNORECASE).group()
            self.result['title'] = bs4.BeautifulSoup(rawMatch, 'html.parser').string
        except:
            self.result['title'] = 'Title not found.'
    
    def countHeadings(self):
        self.result['headings'] = dict()
        for headLevel in range(1, 6): # possible head levels: h1,h2,..,h6
            searchResult = len(re.findall(r'<h{0}'.format(headLevel), self.r.text, re.IGNORECASE|re.MULTILINE))
            if(searchResult > 0):
                self.result['headings']['h{0}'.format(headLevel)] = searchResult
    
    def findAllLinks(self):
        self.result['numOfInternalLinks'] = 0
        self.result['numOfExternalLinks'] = 0
        self.domainName = self.targetUrl.split('//')[-1].split('.')[1]

        # find ALL links in the document
        self.allLinks = re.findall(r'"((http|ftp|https)s?://.*?)"', self.r.text, re.IGNORECASE|re.MULTILINE)
    
    def groupLinks(self): # to external/internal links
         # check if they are internal or external links and count them
        for link in self.allLinks:
            if self.domainName.lower() in link[0].lower():
                self.result['numOfInternalLinks'] += 1
            else:
                self.result['numOfExternalLinks'] += 1
    
    def getInaccessibleLinks(self):
        # Are there any inaccessible links and how many?
        inaccessibleLinks = list()
        for link in self.allLinks:
            # just ask for the header in order to save time
            statusCode = requests.head(link[0]).status_code
            if statusCode >= 400 and statusCode <= 450:
                inaccessibleLinks.append(link[0])
        
        self.result['inaccessibleLinks'] = len(inaccessibleLinks)
    
    def findLoginForm(self):
        # Did the page contain a login-form? 
        rawMatch = re.findall(r'<form\b[^>]*>(.*?)<\/form>', self.r.text, re.IGNORECASE|re.MULTILINE|re.S)
        loginFormKeyWords = [r'login', r'sign in', r'sign-in', r'username', r'password']
        isLoginForm = False
        for match in rawMatch:
            for keyWord in loginFormKeyWords:
                if keyWord in match.lower():
                    isLoginForm = True
                    break
        
        if isLoginForm:
            self.result['containsLoginForm'] = 'Yes.'
        else:
            self.result['containsLoginForm'] = 'No form found.'