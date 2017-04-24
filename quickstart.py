import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

from datetime import datetime
from dateutil import tz
import re


try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
# Science
#https://www.googleapis.com/auth/calendar.readonly
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def get_calendars():

    print('Getting the calendar list')
    page_token = None
    calendars = []
    while True:
      calendar_list = service.calendarList().list(pageToken=page_token).execute()
      for calendar_list_entry in calendar_list['items']:
        calendar = [calendar_list_entry['id'], calendar_list_entry['summary'], calendar_list_entry['timeZone']]
        calendars.append(calendar)
      page_token = calendar_list.get('nextPageToken')
      if not page_token:
        break

    return calendars

def get_calendar(service, calendar_id):

    print('Getting the AMA calendar')
    print('-----------------------')
    calendar_list_entry = service.calendarList().get(calendarId=calendar_id).execute()

    return

def get_events(service, calendar_id, time_min, from_zone, to_zone):

    print('Getting the upcoming 25 events')
    print('-----------------------')
    eventsResult = service.events().list(
        calendarId='amaverify@gmail.com', timeMin=time_min, maxResults=25, singleEvents=True,
        orderBy='startTime').execute()
    events = eventsResult.get('items', [])

    amas = []
    if not events:
        print('No upcoming events found.')
    for event in events:
        st = convert_datetime(event['start'].get('dateTime'), from_zone, to_zone)
        et = convert_datetime(event['end'].get('dateTime'), from_zone, to_zone)
        e_id = event['id']
        status = event['status']
        summary = event['summary']
        description = event['description']
        ama = [e_id, st, et, status, summary, description]
        #print(ama)

    return amas

def convert_datetime(timestamp, from_zone, to_zone):

    # THIS SPLITS THIS '2017-11-05T05:00:00-05:00' INTO THIS ['2017-11-05', '05:00:00', '05:00']
    split = re.split('[A-Z]|(?<=)-(?=[0-9]{2}:)', timestamp)
    dt = datetime.strptime(' '.join((split[0], split[1])), '%Y-%m-%d %H:%M:%S')
    dt = dt.replace(tzinfo=from_zone)
    gmt = dt.astimezone(to_zone)
    gmt = datetime.strftime(gmt, '%Y-%m-%d %H:%M:%S')

    return gmt

def main():
    """Shows basic usage of the Google Calendar API.

    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    now = datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    uk_zone = tz.gettz('Europe/London')
    est_zone = tz.gettz('America/New_York')

    iama = 'amaverify@gmail.com'
    calendar = get_calendar(service, iama)

    events = get_events(service, iama, now, est_zone, uk_zone)


if __name__ == '__main__':
    main()
