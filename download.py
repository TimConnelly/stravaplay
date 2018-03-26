import stravalib
from http.server import BaseHTTPRequestHandler,HTTPServer
import urllib.parse
import urllib.request
import datetime
import requests
import webbrowser
from threading import Thread
import pandas as pd
import time

client_id, secret = open('client.secret').read().strip().split(',')
port = 5000
url = 'http://localhost:%d/authorized' % port
done = False
types = ['time', 'distance', 'latlng', 'altitude', 'velocity_smooth', 'moving', 'grade_smooth', 'temp']
limit = 1

client = stravalib.client.Client()
authorize_url = client.authorization_url(client_id=client_id, redirect_uri=url)

class MyHandler(BaseHTTPRequestHandler):

    def do_HEAD(self):
        return self.do_GET()

    def do_GET(self):
        global done
        if done:
            return
        self.wfile.write(b'<script>window.close();</script>')
        code = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)['code'][0]

        access_token = client.exchange_code_for_token(
            client_id=client_id,
            client_secret=secret,
            code=code
        )

        client.access_token = access_token
        athlete = client.get_athlete()
        print(
            "For %(id)s, I now have an access token %(token)s" %
            {'id': athlete.id, 'token': access_token}
        )

        activities = client.get_activities()
        date, distance, elevation = zip(*[
            (a.start_date, a.distance.num, a.total_elevation_gain.num)
            for a in activities
            if a.type == 'Run'
        ])

        df = pd.DataFrame(dict(
            date = date, distance = distance, elevation = elevation
        ))
        df.to_pickle('data.pkl')

        done = True

print('Opening: %s' % authorize_url)
webbrowser.open(authorize_url)
httpd = HTTPServer(('localhost', port), MyHandler)
while not done:
    httpd.handle_request()
