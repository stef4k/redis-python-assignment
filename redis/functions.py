# importing the necessary libraries
from tinydb import TinyDB, Query
import redis
import datetime
from datetime import datetime as datetime2

# global variables
eventID = 7  # global variable for eventID in database eventsLog
db_users = None
db_meetings = None
db_meeting_instances = None
db_eventsLog = None
client = None


def start():
    """
    Function to connect to databases and client

    Returns
    -------
    None.
    """
    # connect to redis server
    ip_address = '127.0.0.1'
    global client
    client = redis.Redis(host=ip_address, port='6379')
    # connect to database files
    global db_users, db_meetings, db_meeting_instances, db_eventsLog
    db_users = TinyDB('users.json')
    db_meetings = TinyDB('meetings.json')
    db_meeting_instances = TinyDB('meeting_instances.json')
    db_eventsLog = TinyDB('eventsLog.json')


def activate_meeting(meetingID):
    """
    Function that checks the particular meeting instance from the database table 
    meeting instances and activates the meeting with @meetingID if it should be live at 
    particular moment (meaning the current date is before the end of the instance 
    and after the start of it). The meeting instances is being activated by
    saving the meetingID inside a set in redis named @active

    Parameters
    ----------
    meetingID: str
        Id of the meeting

    Returns
    -------
    None
    """
    if not check_meeting_exists(meetingID):
        print('Meeting with ID ' + meetingID + ' not found in database')
    elif client.sismember('active', meetingID):
        print(get_meeting_title(meetingID) + ' meeting already active')
    else:
        # iterate through all meeting instances in database @meeting_instances
        for instance in db_meeting_instances:
            if instance['meetingID'] == meetingID:
                start_date = datetime.datetime.strptime(
                    instance['fromdatetime'], '%Y-%m-%d %H:%M:%S.%f')
                finish_date = datetime.datetime.strptime(
                    instance['todatetime'], '%Y-%m-%d %H:%M:%S.%f')
                # date now must be between the start and end date of the meeting instance
                if (start_date < datetime.datetime.now()) & (finish_date > datetime.datetime.now()):
                    # add the meetingID to the redis set  @active
                    client.sadd('active', instance['meetingID'])
                    print('Meeting instance for ' + get_meeting_title(meetingID) +
                          ' activated!')
                    return
        print('No meeting instance for ' + get_meeting_title(meetingID) +
              ' planned for this moment')


def show_active_meetings():
    """   
    Function that prints the information of active meetings. It iterates through
    the redis set @active and for each different meetingID value there, the information
    of the particular meetingID is printed from the database @meetings.
    If active meetings are found in the set @active, a relative message is printed.

    Returns
    -------
    bool
        True if there is at least one active meeting. False, if not.
    """
    # iterate through all active meetingIDS
    for meeting in client.smembers('active'):
        meetingID = meeting.decode('utf-8')
        # print for each meetingID the extended information
        print(meetingID + '| ' + get_meeting_title(meetingID) +
              ': ' + get_meeting_description(meetingID))
    if len(client.smembers('active')) == 0:
        print('No active meetings at the moment.')
        return False
    return True


def join_meeting(meeting_id, user_id):
    """
    A user joins an active meeting.

    Parameters
    ----------
    meeting_id: str
        Id of the meeting
    user_id: str
        Id of the user

    Returns
    -------
    None
    """
    if check_user_exists(user_id):
        participants = meeting_id + '_participants'
        # audience = get_meeting_audience(meeting_id)
        if not get_meeting_publicity(meeting_id):
            if get_user_email(user_id) in get_meeting_audience(meeting_id):
                if not client.hexists(participants, user_id):
                    timestamp = round(datetime2.timestamp(datetime2.now()))
                    client.hset(participants, user_id, timestamp)
                    print('{user} just joined {meeting}!'
                          .format(user=get_user_name(user_id), meeting=get_meeting_title(meeting_id)))

                    # update event log
                    insert_eventLog(user_id, 1, timestamp)
                else:
                    print(get_user_name(user_id), '{user} can not double-join {meeting}.'
                          .format(user=get_user_name(user_id), meeting=get_meeting_title(meeting_id)))
                return
            print('Email ({email}) of {user}, is not in the audience of {meeting}.'
                  .format(email=get_user_email(user_id),
                          user=get_user_name(user_id),
                          meeting=get_meeting_title(meeting_id)
                          ))
            return
        else:
            if not client.hexists(participants, user_id):
                timestamp = round(datetime2.timestamp(datetime2.now()))
                client.hset(participants, user_id, timestamp)
                print('{user} just joined {meeting}!'
                      .format(user=get_user_name(user_id), meeting=get_meeting_title(meeting_id)))

                # update event log
                insert_eventLog(user_id, 1, timestamp)
            else:
                print('{user} is already participating at {meeting}.'
                      .format(user=get_user_name(user_id), meeting=get_meeting_title(meeting_id)))
            return
    print('User with ID {user_id} does not exist in database.'.format(user_id=user_id))


def leave_meeting(meeting_id, user_id):
    """
    A user leaves a meeting, if he already participates at it.

    Parameters
    ----------
    meeting_id: str
        Id of the meeting
    user_id: str
        Id of the user

    Returns
    -------
    None
    """
    if check_user_exists(user_id):
        if client.hexists(meeting_id + '_participants', user_id):
            client.hdel(meeting_id + '_participants', user_id)

            # update event log
            timestamp = round(datetime2.timestamp(datetime2.now()))
            insert_eventLog(user_id, 2, timestamp)
            print('{user} just left {meeting}.'
                  .format(user=get_user_name(user_id), meeting=get_meeting_title(meeting_id)))

        else:
            print('{user} is not currently participating at {meeting}.'
                  .format(user=get_user_name(user_id), meeting=get_meeting_title(meeting_id)))
        return
    print('User with ID {user_id} does not exist in database.'.format(user_id=user_id))


def show_meeting_current_participants(meeting_id):
    """
    Shows all the users that are participating in a specific meeting.

    Parameters
    ----------
    meeting_id: str
        Id of the meeting

    Returns
    -------
    bool
        True, if all checks pass. False, if not.
    """
    participants = meeting_id + '_participants'
    if client.sismember('active', meeting_id):
        if client.hlen(participants) != 0:
            print('Participants of {meeting_title}:'.format(meeting_title=get_meeting_title(meeting_id)), end='| ')
            for user in client.hkeys(participants):
                print('#' + user.decode('utf-8'), get_user_name(user.decode('utf-8')), end=' | ')
            print()
            return True
        else:
            print('Nobody participates at {meeting_title} yet.'.format(meeting_title=get_meeting_title(meeting_id)))
            return False
    print(meeting_id + ' {meeting} is not an active meeting.'.format(meeting=get_meeting_title(meeting_id)))


def show_join_timestamp():
    """
    Shows all participants and the timestamp at which they joined, for all active meetings.

    Returns
    -------
    None
    """
    if client.scard('active') != 0:
        for meeting in client.smembers('active'):
            participants = meeting.decode('utf-8') + '_participants'
            print('{meeting} has {length} participants.'
                  .format(meeting=get_meeting_title(meeting.decode('utf-8')), length=client.hlen(participants)))

            if client.hlen(participants) != 0:
                print('\n'.join(
                    ['#{user_id} {user_name}: joined at {timestamp}'
                         .format(user_id=user.decode('utf-8'),
                                 user_name=get_user_name(user.decode('utf-8')),
                                 timestamp=datetime2.fromtimestamp(int(client.hget(participants, user).decode('utf-8')))
                                 )
                     for user in client.hkeys(participants)
                     ]))
            print()
        return

    print('There are no active meetings at the moment.')


def end_meeting(meeting_id):
    """
    End an active meeting (and kick its participants).

    Parameters
    ----------
    meeting_id: str
        Id of the meeting

    Returns
    -------
    None
    """
    if check_meeting_exists(meeting_id):
        if client.sismember('active', meeting_id):
            participants = meeting_id + '_participants'
            if client.hlen(participants) != 0:
                for user in client.hkeys(participants).copy():
                    # update event log for the participants
                    timestamp = round(datetime2.timestamp(datetime2.now()))
                    insert_eventLog(user.decode('utf-8'), 3, timestamp)
                    client.hdel(participants, user)

            # update event log for the meeting
            timestamp = round(datetime2.timestamp(datetime2.now()))
            insert_eventLog(3, None, timestamp)
            client.srem('active', meeting_id)
            print('{meeting} just ended.'.format(meeting=get_meeting_title(meeting_id)))
            return
        print('#{m_id}{m_title} is not active at the moment.'
              .format(m_id=meeting_id, m_title=get_meeting_title(meeting_id)))
    else:
        print('Meeting with ID {meeting_id} does not exist in database.'
              .format(meeting_id=meeting_id))


def post_message(current_meetingID, userID, message):
    """
    Function that represents a message posting on a meeting. Practically, this 
    function creates or appends to a redis list called 'meetingID_messages' 
    (where meetingID is the meetingID number) a string called 'meetingID_messages_userID_timestamp'
    (where meetingID is the meetingID number, userID is the user's ID and timestamp 
    is the current timestamp) Also a hash is created with the same name 
    @meetingID_messages_timestamp which contains the fields: message  and userID which contain the particular
    message abd userID that sent the message

    Parameters
    ----------
    current_meetingID : str
        Id of the current meeting
    userID : str
        Id of the user
    message : str
        The message the user sent

    Returns
    -------
    bool
        True, if user posts the message. False, if not.

    """
    if not client.hget(current_meetingID + '_participants', userID):
        print('User ' + str(userID) + ' has not joined meeting of ' +
              get_meeting_title(current_meetingID) + '.')
        return False
    else:
        # unique current timestamp
        timestamp = round(datetime2.timestamp(datetime2.now()))
        # creating the names of the list and name of the message
        list_name = current_meetingID + '_messages'
        list_item = current_meetingID + '_message_' + \
                    str(userID) + '_' + str(timestamp)
        # append item to list
        client.rpush(list_name, list_item)
        # create hashes of message and userID for item
        client.hset(list_item, 'message', message)
        client.hset(list_item, 'userID', userID)
        # insert action to eventsLog database
        insert_eventLog(userID, 4, timestamp)
        print('Successfully posted a message!')
        return True


def show_chat(meetingID):
    """
    Functions that prints all the messages of a particular meeting @meetingID
    in a chronological order. This functions iterates through the redis list
    @meetingID_messages and after that for each item list which is also stored 
    as a hash the sender user's ID and message are printed.

    Parameters
    ----------
    meetingID : str
        Id of the meeting

    Returns
    -------
    None
    """
    if check_meeting_exists(meetingID):
        if client.llen(meetingID + '_messages'):
            print('Chat of meeting ' + get_meeting_title(meetingID) +
                  ' :')
            for message in client.lrange(meetingID + '_messages', 0, -1):
                message_name = message.decode('utf-8')
                message_sender = client.hget(message_name, 'userID').decode('utf-8')
                message_text = client.hget(message_name, 'message').decode('utf-8')
                print(get_user_name(message_sender) + ': ' + message_text)
        else:
            print('There are no messages at ' + get_meeting_title(meetingID) + '.')
    else:
        print('Meeting with ID ' + meetingID + ' not found in database.')


def show_user_chat(meetingID, userID):
    """
    Function that prints for a particular meeting and user, all of his/her 
    chat messages in that meeting. It iterates through the list of messages
    for that particular meeting. For each message, it checks if it was sent by
    the particular user and if so, it prints the time together with the message.

    Parameters
    ----------
    meetingID : str
        Id of the meeting
    userID : str
        Id of the user

    Returns
    -------
    None
    """
    # meeting is not active
    if check_user_exists(userID):
        if not client.hget(meetingID + '_participants', userID):
            print('User ' + str(userID) + ' is not participating at ' +
                  get_meeting_title(meetingID) + '.')
        else:
            print('Messages of user ' + get_user_name(userID) + ' in meeting ' +
                  get_meeting_title(meetingID) + ':')
            for message in client.lrange(meetingID + '_messages', 0, -1):
                message_name = message.decode('utf-8')
                message_sender = client.hget(message_name, 'userID').decode('utf-8')
                if (message_sender == userID):
                    message_text = client.hget(message_name, 'message').decode('utf-8')
                    timestamp = message_name[message_name.rindex('_') + 1:]
                    date_timestamp = datetime2.fromtimestamp(int(timestamp))
                    print(str(date_timestamp.time()) + ' : ' + message_text)
        return
    print('User with ID {user_id} does not exist in database.'
          .format(user_id=userID))


def get_eventID():
    """
    Function that returns a unique eventID used in database eventsLog
    Everytime it is called, it increases by 1 and returns a unique eventID.

    Returns
    _______
    int
        Id of the event
    """
    global eventID
    eventID = eventID + 1
    return eventID


def get_meeting_title(meetingID):
    """
    Function that finds the title of a particular @meetingID inside the database
    of meetings

    Parameters
    ----------
    meetingID : str
        Id of the meeting

    Returns
    -------
    str
        The title of the particular meeting
    """
    query = Query()
    result = db_meetings.search(query.meetingID == meetingID)
    return result[0]['title']


def get_meeting_audience(meeting_id):
    """
    Searches and returns the audience of a meeting, based on its id.

    Parameters
    ----------
    meeting_id: str
        Id of the meeting

    Returns
    -------
    str
       The audience of the meeting
    """
    query = Query()
    result = db_meetings.search(query.meetingID == meeting_id)
    return result[0]['audience']


def get_meeting_publicity(meeting_id):
    """
    Searches and returns if a meeting is public, based on its id.

    Parameters
    ----------
    meeting_id: str
        Id of the meeting

    Returns
    -------
    bool
       True, if meeting is public. False, if not.
    """
    query = Query()
    result = db_meetings.search(query.meetingID == meeting_id)
    return result[0]['isPublic']


def get_user_name(user_id):
    """
    Searches and returns the name of a user, based on his id.

    Parameters
    ----------
    user_id: str
        Id of the user

    Returns
    -------
    str
       The name of the user
    """
    query = Query()
    result = db_users.search(query['userID'] == str(user_id))
    return result[0]['name']


def get_user_email(user_id):
    """
    Searches and returns the email of a user, based on his id.

    Parameters
    ----------
    user_id: str
        Id of the user

    Returns
    -------
    str
       The email of the meeting
    """
    query = Query()
    result = db_users.search(query['userID'] == str(user_id))
    return result[0]['email']


def get_meeting_description(meetingID):
    """
    Function that finds the description of a particular @meetingID inside the database
    of meetings

    Parameters
    ----------
    meetingID : str
        Id of the meeting

    Returns
    -------
    str
        The description of the particular meeting
    """
    query = Query()
    result = db_meetings.search(query.meetingID == meetingID)
    return result[0]['description']


def insert_eventLog(userID, event_type, timestamp):
    """
    Function that inserts in the database @eventsLog a particular event
    from a particular user @userID, of a particular @event_type and the particular
    time it happened

    Parameters
    ----------
    userID : str
    event_type : {1, 2, 3, 4}
        1 for user joining a meeting, 2 for user leaving a meeting,
        3 for a meeting ending, 4 for a user posting a message
    timestamp : int

    Returns
    -------
    None

    """
    db_eventsLog.insert({'event_id': get_eventID(), 'userID': userID,
                         'event_type': event_type, 'timestamp': timestamp})


def check_meeting_active(meetingID):
    """
    Function that checks if the meeting with @meetingID is active (meaning is
    inside the redis set @active). Returns true if meeting is active

    Parameters
    ----------
    meetingID : str
        Id of the meeting

    Returns
    -------
    bool
        True, if meeting is active. False, if not.
    """
    return True if client.sismember('active', meetingID) else False


def check_user_exists(userID):
    """
    Function that checks if a user with @userID exists in the database users

    Parameters
    ----------
    userID : str
        Id of the user

    Returns
    -------
    bool
        True, if user exists in database. False, if not.
    """
    query = Query()
    result = db_users.search(query.userID == userID)
    return True if len(result) > 0 else False


def check_meeting_exists(meetingID):
    """
    Function that checks if a meeting with @meetingID exists in the database 
    meetings

    Parameters
    ----------
    meetingID : str
        Id of the meeting

    Returns
    -------
    bool
        True, if meeting exists in database. False, if not.
    """
    query = Query()
    result = db_meetings.search(query.meetingID == meetingID)
    return True if len(result) > 0 else False


def print_menu():
    """
    Functions that prints the menu of the meeting application

    Returns
    -------
    None
    """
    print('---' * 15)
    print('\t\t~ Menu ~\n'
          'Press:\n'
          '1: Activate a meeting instance\n' +
          '2: Show active meetings\n' +
          '3: Join an active meeting\n' +
          '4: Leave a meeting\n' +
          '5: Show meetings current participants\n' +
          '6: End a meeting\n'
          '7: Post a chat message\n' +
          '8: Show the chat of a meeting\n'
          '9: Show for active meetings when current participants joined\n' +
          '10: Show the messages of a user in a active meeting\n'
          'X: Exit application')
    print('---' * 15)


def print_all_users():
    """
    Function that prints all users IDs, name and age from db_users

    Returns
    -------
    None
    """
    for user in db_users:
        print(user['userID'] + '| ' + user['name'] + ', ' + str(user['age'])
              + ' years old')


def print_all_meetings():
    """
    Function that prints all meeting IDs, title and description from db_meetings

    Returns
    -------
    None
    """
    for meeting in db_meetings:
        print(meeting['meetingID'] + '| ' + meeting['title'] + ': ' +
              meeting['description'])


def close():
    """
    Function to close connection to database and delete redis server inserts

    Returns
    -------
    None
    """
    global db_users, db_meetings, db_meeting_instances, db_eventsLog, client
    client.flushall()
    db_users.close()
    db_meetings.close()
    db_meeting_instances.close()
    db_eventsLog.close()
