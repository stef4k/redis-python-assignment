from tinydb import TinyDB

#create the new databases in json files
db_users = TinyDB('users.json')
db_meetings = TinyDB('meetings.json')
db_meeting_instances = TinyDB('meeting_instances.json')
db_eventsLog =  TinyDB('eventsLog.json')

#inserting data in users database
db_users.insert({'userID': '1', 'name': 'John Collins','age': 21,
                 'gender':'male', 'email':'collins1@gmail.com'})
db_users.insert({'userID': '2', 'name': 'Jack Johnson','age': 30,
                 'gender':'male', 'email':'ohnson@gmail.com'})
db_users.insert({'userID': '3', 'name': 'Kate Daniels','age': 35,
                 'gender':'female', 'email':'kate91@gmail.com'})
db_users.insert({'userID': '4', 'name': 'Ellie Dodgers','age': 23,
                 'gender':'female', 'email':'elliex@gmail.com'})
db_users.insert({'userID': '5', 'name': 'Stef Rodrigez','age': 29,
                 'gender':'male', 'email':'stef_rod@hotmail.com'})
db_users.insert({'userID': '6', 'name': 'Nina Jackson','age': 18,
                 'gender':'female', 'email':'ninaa100@gmail.com'})

#inserting data in meetings database
db_meetings.insert({'meetingID': '100', 'title': 'Algorithms',
                    'description': 'Lecture on algotithms and data structures',
                    'isPublic': False, 'audience': [2,5,6]})
db_meetings.insert({'meetingID': '200', 'title': 'Databases',
                    'description': 'Lecture on relational databases',
                    'isPublic': True, 'audience': None})
db_meetings.insert({'meetingID': '300', 'title': 'Machine learning',
                    'description': 'Introductory lecture on data analysis '+
                    'and machine learning',
                    'isPublic': False, 'audience': [1,2,3,4]})
db_meetings.insert({'meetingID': '400', 'title': 'CV Guide',
                    'description': 'A guide on how to make a competitice CV',
                    'isPublic': True, 'audience': None})

#inserting data in meetings instances database
db_meeting_instances.insert({'meetingID':'100', 'orderID': 1,
                             'fromdatetime': '2021-03-24 22:59:53.109391',
                             'todatetime':'2021-03-25 22:59:53.109391'})
db_meeting_instances.insert({'meetingID':'100', 'orderID': 2,
                             'fromdatetime': '2021-04-24 22:59:53.109391',
                             'todatetime':'2021-05-24 22:59:53.109391'})
db_meeting_instances.insert({'meetingID':'200', 'orderID': 1,
                             'fromdatetime': '2021-04-20 12:59:53.109391',
                             'todatetime':'2021-05-20 22:00:53.109391'})
db_meeting_instances.insert({'meetingID':'300', 'orderID': 1,
                             'fromdatetime': '2021-04-22 12:00:00.109391',
                             'todatetime':'2021-06-01 12:00:53.109391'})
db_meeting_instances.insert({'meetingID':'400', 'orderID': 1,
                             'fromdatetime': '2021-01-01 22:59:53.109391',
                             'todatetime':'2021-01-01 23:59:53.109391'})
db_meeting_instances.insert({'meetingID':'400', 'orderID': 2,
                             'fromdatetime': '2021-02-01 22:59:53.109391',
                             'todatetime':'2021-06-01 22:59:53.109391'})


#inserting data in events log database
db_eventsLog.insert({'event_id': 1, 'userID': 1,
                     'event_type':1, 'timestamp':'1619298979.5193353'})
db_eventsLog.insert({'event_id': 2, 'userID': 2,
                     'event_type':1, 'timestamp':'1619298968.5193353'})
db_eventsLog.insert({'event_id': 3, 'userID': 1,
                     'event_type':4, 'timestamp':'1619298978.5111353'})
db_eventsLog.insert({'event_id': 4, 'userID': 2,
                     'event_type':1, 'timestamp':'1619298975.5193353'})
db_eventsLog.insert({'event_id': 5, 'userID': 4,
                     'event_type':1, 'timestamp':'1619298970.5193353'})
db_eventsLog.insert({'event_id': 6, 'userID': 4,
                     'event_type':2, 'timestamp':'1619298978.5193353'})

                  
#close connection to databasefiles
db_users.close()
db_meetings.close()
db_meeting_instances.close()
db_eventsLog.close()