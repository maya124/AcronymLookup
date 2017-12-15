# app.py
#
# This file creates a simple web application to look up acronym definitions.
# The app can be run with `gunicorn app:app`

import cgi
import loadPickles
import serve

# app() - sets up a WSGI (Web Server Gateway Interface) compliant web app.
# Given a POST request containing a string of words, this function returns a
# string mapping all acronyms in the string to their predicted meanings.
def app(environ, start_fn):
    if environ['REQUEST_METHOD'] == 'POST':
        post_env = environ.copy()
        post_env['QUERY_STRING'] = ''
        post = cgi.FieldStorage(
            fp=environ['wsgi.input'],
            environ=post_env,
            keep_blank_values=True
        )
        results = serve.predict(post['selection'].value)['results']
        print("results: ", results)
        start_fn('200 OK', [('Content-Type', 'text/plain')])
        return [results]
    else:
        return ['invalid request']
        
