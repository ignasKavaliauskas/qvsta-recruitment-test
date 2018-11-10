# qvsta-recruitment-test
The objective is to build a rest backend that does some analysis of a web-page/URL.

# Tasks
- [x] The backend should receive the URL of the webpage being analyzed as a parameter. 
- After the processed results should be returned to the user. The result comprises the following information:
- - [x] What HTML version has the document?
- - [x] What is the page title?
- - [x] How many headings of what level are in the document?
- - [x] How many internal and external links are in the document? Are there any inaccessible links and how many?
- - [ ] Did the page contain a login-form?
- - [x] Return error message in case of a unreachable URL, including HTTP status-code and some useful error description.

# How to run
Requirements:
- python 3.7
- pip
- pipenv

Clone this repository and run it by using these commands:(make sure you're in the repository)
- `pipenv install`
- `pipenv shell`
- `python manage.py runserver`
