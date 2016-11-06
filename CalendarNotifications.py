#!/usr/bin/env python
import gflags
import httplib2
import datetime
from googleapiclient.discovery import  build
from oauth2client.file import Storage
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import *
from ConfigParser import *

from Logger import *
logger = setupLogging(__name__)
logger.setLevel(INFO)

configFile = u"ComputerVision.conf"
Config = ConfigParser()
Config.read(configFile)

verification_code = ConfigSectionMap(u"PCV", Config)[u'verification_code']
client_id = ConfigSectionMap(u"PCV", Config)[u'client_id']
client_secret = ConfigSectionMap(u"PCV", Config)[u'client_secret']


if __name__ == u"__main__":

    FLAGS = gflags.FLAGS

    FLOW = OAuth2WebServerFlow(
        client_id = client_id,
        client_secret = client_secret,
        scope = u'https://www.googleapis.com/auth/calendar',
        user_agent = u'[USER AGENT]/1.0'
        )

    storage = Storage(u'calendar_creds.dat')
    credentials = storage.get()
    if credentials is None or credentials.invalid == True:
        credentials = run_flow(FLOW, storage)

    http = httplib2.Http()
    http = credentials.authorize(http)

    service = build(serviceName = u'calendar', version = u'v3', http = http,
                    developerKey = u'AIzaSyDq0KBBoYlAQhGnShuVk--EpkHYf8bznas')

    startdatetime = str(datetime.datetime.now().strftime(u'%Y-%m-%dT00:00:00+05:30'))
    enddatetime = str(datetime.datetime.now().strftime(u'%Y-%m-%dT23:59:59+05:30'))

    page_token = None
    while True:
        events = service.events().list(calendarId = u'primary',
                                       pageToken = page_token,
                                       timeMin = startdatetime,
                                       timeMax = enddatetime).execute()

        for event in events[u'items']:
            print("{0}{1}".format(event, os.linesep))
            if isinstance(event, dict):
                for k, v in event.items():
                    print("event[{0}] = {1}".format(k, v))

            print("----------------------------------------------------------")
        page_token = events.get(u'nextPageToken')
        if not page_token:
            break

