# qvsta-recruitment-test
The objective is to build a rest backend that does some analysis of a web-page/URL.

# Tasks
- [x] The backend should receive the URL of the webpage being analyzed as a parameter. 
- After the processed results should be returned to the user. The result comprises the following information:
- - [x] What HTML version has the document?
- - [x] What is the page title?
- - [x] How many headings of what level are in the document?
- - [x] How many internal and external links are in the document? Are there any inaccessible links and how many?
- - [x] Did the page contain a login-form?
- - [x] Return error message in case of a unreachable URL, including HTTP status-code and some useful error description.
- [x] Cache already scrapped results for 24h.
# Main steps of building my solution
- Learn all necessary Django features and functions required for this project
- Starting and preparing the project, createing the files, virtual enviroment and downloading possibly required librarys
- Working off the tasks step by step
- Was not sure about the HTML version questions at the beginning, since not all webpages contain a <!doctype> line, so when this line was present, it'll return the line, otherwise it'll just tell you that no version was found. Also checked out the headers but couldn't find the version there as well.
- The internal/external links questions was kinda tricky. I was trying to have a nice match using regular expressions for both type of links but I haven't figured out a great way of finding all internal links, since internal links have different formats and how they link you to the next page. The external links have just one format wich made it easier for me. At the end I decided to collect ALL links contained on the website and group them by the domain name. All links containing the domain name of the target URL are identified as a internal link, and the other as external. It's not the best solution since it's not covering every pattern but it's the best one i came up with right now. I have left the previous solution commented inside the view.
- The project took me about 10h in total.
- The biggest and most time consuming parts of the projects was getting into Django and creating/modyfing the regular expressions.
- The biggest execution delay is caused by searching for inaccessible links.

All features needs to be more tested in order guarantee correct functioning.
# How to run
Requirements:
- python 3.7
- pip
- pipenv

Clone this repository and run it by using these commands:
- `pipenv install`
- `pipenv shell`
- `python manage.py runserver`
