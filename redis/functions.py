# importing the necessary libraries
from tinydb import TinyDB, Query
import redis
import datetime
import pprint


# connect to redis server
ip_address = '192.168.1.3'
client = redis.Redis(host = ip_address, port = '6379')


# connect to database files
db_users = TinyDB('users.json')
db_meetings = TinyDB('meetings.json')
db_meeting_instances = TinyDB('meeting_instances.json')
db_eventsLog = TinyDB('eventsLog.json')


def activate_meetings():
    """
    Function that checks all the meeting instances from the database table 
    meeting instances and activates the ones that should be live at the 
    particular moment (meaning the current date is before the end of the instance 
    and after the start of it). Meeting instances are being activated by
    saving the meetingID inside a set in redis named @active
    
    Returns: -
    """
    # iterate through all meeting instances in database @meeting_instances
    for instance in db_meeting_instances:
        start_date = datetime.datetime.strptime(instance['fromdatetime'], '%Y-%m-%d %H:%M:%S.%f')
        finish_date = datetime.datetime.strptime(instance['todatetime'], '%Y-%m-%d %H:%M:%S.%f')
        # date now must be between the start and end date of the meeting instance
        if ((start_date < datetime.datetime.now()) & (finish_date > datetime.datetime.now() )):
            # add the meetingID to the redis set  @active
            client.sadd('active', instance['meetingID'])


def show_active_meetings():
    """   
    Function that prints the information of active meetings. It iterates through
    the redis set @active and for each different meetingID value there, the information
    of the particular meetingID is printed from the database @meetings
    Returns: -
    """
    query = Query()
    # iterate through all active meetingIDS
    for meeting in client.smembers('active'):
        # print for each meetingID the extended information
        pprint.pprint(db_meetings.search(query.meetingID == meeting.decode('utf-8')))


# test functions
activate_meetings()
show_active_meetings()

# close connection to database files
db_users.close()
db_meetings.close()
db_meeting_instances.close()
db_eventsLog.close()
