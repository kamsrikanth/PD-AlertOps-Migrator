from tkinter import *
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import messagebox
import tkinter as tk
import requests
import json
import ast
import sys
from collections import OrderedDict
import threading

#Declaring PagerDuty API KEY for global usage
def declare_a_global_pdkey(api_key):
    global pd_api_key
    pd_api_key = api_key

#Declaring AlertOps' V2 API KEY for global usage
def declare_a_global_aokey(api_key):
    global ao_api_key
    ao_api_key = api_key

#This function creates the log area where messages corresponding to different
#API Callbacks are displayed for log and debugging purposes
def createlogArea():
    #pb.start()
    global h
    global v
    h = Scrollbar(ws, orient = 'horizontal')
    h.pack(side = BOTTOM, fill = X)
    v = Scrollbar(ws)
    v.pack(side = RIGHT, fill = Y)
    global t
    t = Text(ws, width = 15, height = 15, wrap = NONE,
                                 xscrollcommand = h.set,
                                 yscrollcommand = v.set)
    t.pack(side=TOP, fill=X, expand=True)
    h.config(command=t.xview)
    v.config(command=t.yview)

#This function is used to take the selected Teams from PD for Migration
#If there are no teams selected, then just the users are transferred automatically
#else groups are first added to AO, then members of the group are retrieved, and
#only those members are added as users in AO
def show_selected():
    t.config(state="normal")
    json_data = {}
    groupsToBeAdded = [] #list variable to store just the selected PagerDuty groups to be added
    uIds = [] #list variable to store uIds of the PagerDuty members in the group

    #if there is no selection of groups, just transfer users.
    if not tv.selection():
        t.insert(END, "- No Groups selected - Transferring just users available \n")
        getUsersFromPD()
    else:
        for i in tv.selection(): #Loop through every PagerDuty group selection one by one
            groupNamesSelected = tv.item(i)
            json_data = groupNamesSelected["values"][3]
            json_data = ast.literal_eval(json_data)
            addGroupstoAO(json_data) #once you get the selected PagerDuty group, first add that to AO
            groupsToBeAdded.append(json_data['name'])
            ids = listMembersOfgroup(json_data,uIds) #Get the members (ids) of the group

        ids = list(list(OrderedDict.fromkeys(ids)))

        for id in ids: #Loop for each user
            userobj = getUser(id) #get entire user object that contains all details
            addUserToAO(userobj,groupsToBeAdded) #add that user to the group
        t.config(state="disabled")
        pb.stop()

#Function to list users of a Team in PagerDuty
def listMembersOfgroup(team,uIds):
    id = team['id']
    print(id)
    url = f'https://api.pagerduty.com/teams/{id}/members'

    payload={}
    headers = {
      'Authorization': 'Token token='+pd_api_key
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    json_data = json.loads(response.text)
    for user in json_data['members']:
        uIds.append(user['user']['id'])
    return uIds

#Function to retrieve user specific information from PagerDuty
def getUser(id):
    url = f'https://api.pagerduty.com/users/{id}'
    payload={}
    headers = {
      'Authorization': 'Token token='+pd_api_key
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    json_data = json.loads(response.text)
    return json_data

#Function to retrieve contact methods of each user in PagerDuty
def getContactMethods(uid):
    url = f'https://api.pagerduty.com/users/{uid}/contact_methods'
    payload={}
    headers = {
      'Authorization': 'Token token='+pd_api_key
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    json_data = json.loads(response.text)
    if response.status_code == 200 or response.status_code == 201:
        print("Retrieved User Contact Methods from PagerDuty...")
        t.insert(END, "- Retrieved User Contact Methods from PagerDuty...\n")
    else:
        print("There was some error retrieving user contact methods from PagerDuty, Error Code: ", response.status_code)
        t.insert(END, "- There was some error retrieving user contact methods from PagerDuty, Error Code: "+str(response.status_code)+"\n")
        sys.exit()
    return json_data


#Function top format email contact method from PagerDuty and make the
#payload compatible to AlertOps for migrating them, DEFAULT Email-Official
#method is needed for AlertOps' users
def formatEmail(label, address):
    if label == "Work" or label == "Pager" or label == "Other":
        AOLabel = "Email-Official"
    else:
        AOLabel = "Email-Personal"

    data_set = {
          "contact_method_name": "Email-Official",
          "email": {
            "email_address": address
          },
          "phone": "None",
          "sms": "None",
          "gateway": "None",
          "push_notification": "None",
          "slack_dm": "None",
          "wait_time_in_mins": 0,
          "repeat": False,
          "repeat_times": 0,
          "repeat_minutes": 0,
          "notification_time24x7": "None",
          "notification_times": "None",
          "enabled": True,
          "sequence": 1
        }
    return data_set

#Function top format phone contact method from PagerDuty and make the
#payload compatible to AlertOps for migrating them
def formatPhone(label, address, country_code):
    if label == "Work" or label == "Skype" or label == "Other":
        AOLabel = "Phone-Official"
    else:
        AOLabel = "Phone-Personal"
    data_set = {
          "contact_method_name": AOLabel,
          "email": "None",
          "phone": {
            "country_code": country_code,
            "phone_number": address,
            "extension": ""
          },
          "sms": "None",
          "gateway": "None",
          "push_notification": "None",
          "slack_dm": "None",
          "wait_time_in_mins": 0,
          "repeat": "None",
          "repeat_times": 0,
          "repeat_minutes": 0,
          "notification_time24x7": "None",
          "notification_times": "None",
          "enabled": True,
          "sequence": 2
        }
    return data_set

#Function top format SMS contact method from PagerDuty and make the
#payload compatible to AlertOps for migrating them
def formatSMS(label, address, country_code):
    if label == "Mobile":
        AOLabel = "SMS-Official"
    else:
        AOLabel = "SMS-Personal"
    data_set = {
          "contact_method_name": AOLabel,
          "email":"None",
          "phone": "None",
          "sms": {
            "country_code": country_code,
            "phone_number": address
          },
          "gateway": "None",
          "push_notification": "None",
          "slack_dm": "None",
          "wait_time_in_mins": 0,
          "repeat": False,
          "repeat_times": 0,
          "repeat_minutes": 0,
          "notification_time24x7": True,
          "notification_times": "None",
          "enabled": True,
          "sequence": 3
        }
    return data_set

#Function top format Push-Notification contact method from PagerDuty and make the
#payload compatible to AlertOps for migrating them
def formatPush(label, address, device_type):
    data_set = {
          "contact_method_name": "Push Official",
          "email": "None",
          "phone": "None",
          "sms": "None",
          "gateway": "None",
          "push_notification": {
                "Platform":device_type
          },
          "slack_dm": "None",
          "wait_time_in_mins": 0,
          "repeat": False,
          "repeat_times": 0,
          "repeat_minutes": 0,
          "notification_time24x7": True,
          "notification_times": "None",
          "enabled": True,
          "sequence": 4
        }
    return data_set


#Functiopn to add user to AlertOps - first get contact methods, format them,
#add them to the payload and then add the users
#This function also calls the method to add users to their respective groups as well
def addUserToAO(user,groupsToBeAdded):
    url = "https://api.alertops.com/api/v2/users"


    #Formatting the name to get the first name, last name and username
    nameOriginal = user['user']['name']
    nameSplit = nameOriginal.split() #assuming a single firstname and lastname, first name will be nameSplit[0], lastname will be nameSplit][1]
    username = user['user']['email'] #username is the email
    #username = f'{nameSplit[0]}_{user["id"]}'
    if len(nameSplit) == 1:
        nameSplit.append(nameSplit[0][0])

    contact_String = []
    #Formatting Contact Methods array
    contactMethods_json = getContactMethods(user['user']['id'])
    for cm in contactMethods_json['contact_methods']:
        if cm['type'] == 'email_contact_method':
            formatString1 = formatEmail(cm['label'],cm['address'])
            contact_String.append(formatString1)

        if cm['type'] == 'phone_contact_method':
            formatString2 = formatPhone(cm['label'],cm['address'],cm['country_code'])
            contact_String.append(formatString2)

        if cm['type'] == 'sms_contact_method':
            formatString3 = formatSMS(cm['label'],cm['address'],cm['country_code'])
            contact_String.append(formatString3)

        if cm['type'] == 'push_notification_contact_method':
            formatString4 = formatPush(cm['label'],cm['address'],cm['device_type'])
            contact_String.append(formatString4)



    payload = json.dumps({
      "user_name": username,
      "first_name": nameSplit[0],
      "last_name": nameSplit[1],
      "locale": "en-US",
      "time_zone": "Central Standard Time",
      "type": "Standard",
      "contact_methods":
        contact_String
      ,
      "roles": [
        "Basic Admin"
      ]
    })


    headers = {
      'api-key': ao_api_key,
      'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    json_data = json.loads(response.text)
    if response.status_code == 200 or response.status_code == 201:
        print("Users added to AlertOps...")
        t.insert(END,"- Users added to AlertOps...\n")
    elif response.status_code == 401:
        print("Unauthorized... Invalid API Key ???")
        t.insert(END, "- Unauthorized... Invalid API Key ??? \n")
    else:
        print("There was some error adding User " +username+ " to AlertOps, Error Message: ", json_data['errors'])
        t.insert(END,"- There was some error adding User " +username+ " to AlertOps, Error Message: "+ str(json_data['errors'])+"\n")

    #add user to their respective groups
    if len(user['user']['teams']) > 0:
        addUserToGroupAO(user,username,groupsToBeAdded)



#Function to retrieve groupID for the group in AlertOps, and then add
#the user to that particular group
def addUserToGroupAO(user,username,groupsToBeAdded):
    teamNames = user['user']['teams']
    for team in teamNames:
        if team['summary'] in groupsToBeAdded:
            gId = getGroupIDFromAO(team) #you need the group ID to add user to a group in AlertOps
            addUserToGID(gId,user,username,team) #once you ger the ID, you can add the user to the groups



#Function to do the API call to retrieve group ID, by giving the groupname
def getGroupIDFromAO(team):
    groupName = team['summary']
    print(groupName)
    url = f'https://api.alertops.com/api/v2/groups?search={groupName}&limit=10&offset=0'
    payload={}
    headers = {
        'api-key': ao_api_key
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    json_data = json.loads(response.text)
    if response.status_code == 200 or response.status_code == 201:
        print("Retrieved group ID in AlertOps to add users...")
        t.insert(END, "- Retrieved group ID in AlertOps to add users...\n")
    elif response.status_code == 401:
        print("Unauthorized... Invalid API Key ???")
        t.insert(END, "- Unauthorized... Invalid API Key ??? \n")
    else:
        print("There was some error retrieving the group IDs to add users, Error Message: ", json_data['errors'])
        t.insert(END, "- There was some error retrieving the group IDs to add users, Error Message: "+ str(json_data['errors'])+"\n")
    if 'groups' in json_data:
        for grid in json_data['groups']:
            if grid['group_name'] == groupName:
                group_id = grid['group_id']
                break
        return group_id



#Function to add user to the group by passing the group ID
def addUserToGID(gID,user,username,team):
    url = f'https://api.alertops.com/api/v2/groups/{gID}/members'
    groupName = team['summary']
    data_set = [
      {
        "member_type": "User",
        "member": username,
        "sequence": 1,
        "roles": [
          "Primary"
        ]
      }
    ]


    payload = json.dumps([
      {
        "member_type": "User",
        "member": username,
        "sequence": 1,
        "roles": [
          "Primary"
        ]
      }
    ])
    headers = {
      'api-key': ao_api_key,
      'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    json_data = json.loads(response.text)
    if response.status_code == 200 or response.status_code == 201:
        print("Added user to Group in AlertOps")
        t.insert(END,"- Added user to Group in AlertOps \n")
    elif response.status_code == 401:
        print("Unauthorized... Invalid API Key ???")
        t.insert(END, "- Unauthorized... Invalid API Key ??? \n")
    else:
        print("There was some error adding user " +username+ " to group "+groupName+" in AlertOps, Error Message: ", json_data['errors'])
        t.insert(END, "- There was some error adding user " +username+ " to group "+groupName+" in AlertOps, Error Message: " +str(json_data['errors'])+"\n")


#Function to add teams retrieved from PagerDuty to alertops
#This is the first step in the migration, you select groups and
#first migrate the groups and then respective users of those groups
def addGroupstoAO(group):
    url = "https://api.alertops.com/api/v2/groups"
    nameOfGroup = group['name']
    description = group['description']

    if description == None or description == "" or description == " ":
        description = "Group migrated from PagerDuty"

    payload = json.dumps({
      "group_name": nameOfGroup,
      "dynamic": "false",
      "description": [
        description
      ],
      "members": [

      ],
      "contact_methods": [

      ],
      "topics": [

      ]
    })

    headers = {
      'api-key': ao_api_key,
      'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    response_data = json.loads(response.text)
    json_data = json.loads(response.text)
    if response.status_code == 200 or response.status_code == 201:
        print("Groups Added to AlertOps ...")
        t.insert(END,"- Groups Added to AlertOps ...\n")
    elif response.status_code == 401:
        print("Unauthorized... Invalid API Key ???")
        t.insert(END,"- Unauthorized... Invalid API Key ???\n")
    else:
        print("There was some error adding group " +nameOfGroup+ " to AlertOps, Error Message: ", json_data['errors'])
        t.insert(END,"- There was some error adding group " +nameOfGroup+ " to AlertOps, Error Message: "+str(json_data['errors'])+"\n")


#Function to retrieve users from PagerDuty and then add jsut the users to AO
def getUsersFromPD():

    url = "https://api.pagerduty.com/users"

    payload={}
    headers = {
      'Authorization': 'Token token='+pd_api_key
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200 or response.status_code == 201:
        print("Retrieved Users from PagerDuty...")
        t.insert(END,"- Retrieved Users from PagerDuty...\n")
    else:
        print("There was some error retrieving users from PagerDuty, Error Code: ", response.status_code)
        t.insert(END, "- There was some error retrieving users from PagerDuty, Error Code: "+ str(response.status_code)+"\n")
        sys.exit()
    json_data = json.loads(response.text)

    for user in json_data['users']:
        addUserToAOWithoutTeams(user)
    t.config(state="disabled")
    pb.stop()


#This function is similar to the previous function for adding users to AlertOps
#Except this function wont call the method to add users to their groups
def addUserToAOWithoutTeams(user):
    url = "https://api.alertops.com/api/v2/users"


    #Formatting the name to get the first name, last name and username
    nameOriginal = user['name']
    nameSplit = nameOriginal.split() #assuming a single firstname and lastname, first name will be nameSplit[0], lastname will be nameSplit][1]
    username = user['email']
    #username = f'{nameSplit[0]}_{user["id"]}'
    if len(nameSplit) == 1:
        nameSplit.append(nameSplit[0][0])

    contact_String = []
    #Formatting Contact Methods array
    contactMethods_json = getContactMethods(user['id'])
    for cm in contactMethods_json['contact_methods']:
        if cm['type'] == 'email_contact_method':
            formatString1 = formatEmail(cm['label'],cm['address'])
            contact_String.append(formatString1)

        if cm['type'] == 'phone_contact_method':
            formatString2 = formatPhone(cm['label'],cm['address'],cm['country_code'])
            contact_String.append(formatString2)

        if cm['type'] == 'sms_contact_method':
            formatString3 = formatSMS(cm['label'],cm['address'],cm['country_code'])
            contact_String.append(formatString3)

        if cm['type'] == 'push_notification_contact_method':
            formatString4 = formatPush(cm['label'],cm['address'],cm['device_type'])
            contact_String.append(formatString4)



    payload = json.dumps({
      "user_name": username,
      "first_name": nameSplit[0],
      "last_name": nameSplit[1],
      "locale": "en-US",
      "time_zone": "Central Standard Time",
      "type": "Standard",
      "contact_methods":
        contact_String
      ,
      "roles": [
        "Basic Admin"
      ]
    })

    headers = {
      'api-key': ao_api_key,
      'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    json_data = json.loads(response.text)
    if response.status_code == 200 or response.status_code == 201:
        print("Users added to AlertOps...")
        t.insert(END, "- Users added to AlertOps...\n")
    elif response.status_code == 401:
        print("Unauthorized... Invalid API Key ???")
        t.insert(END, "- Unauthorized... Invalid API Key ??? \n")
    else:
        print("There was some error adding User " +username+ " to AlertOps, Error Message: ", json_data['errors'])
        t.insert(END, "- There was some error adding User " +username+ " to AlertOps, Error Message: "+ str(json_data['errors'])+"\n")


#Function to show the table of Teams retrieved from PagerDuty
def showTable():

    #Globally declaring the variables for table views, API Keys and labels to access them throughout methods
    global tv
    global entry
    global entry2
    global label
    pd_api_key= entry.get()
    ao_api_key= entry2.get()
    declare_a_global_pdkey(pd_api_key)
    declare_a_global_aokey(ao_api_key)

    #Create TreeView to display teams from PagerDuty
    tv = ttk.Treeview(
        ws,
        columns=(1, 2, 3),
        show='headings',
        height=5
        )
    tv.pack()

    tv.heading(1, text='PD Team Name')
    tv.heading(2, text='ID')
    tv.heading(3, text='Description')

    #URL to retrieve Teams from PagerDuty
    url = "https://api.pagerduty.com/teams"

    payload={}
    headers = {
      'Authorization': 'Token token='+pd_api_key
    }


    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 401 or response.status_code == 404:
        print("Unauthorized... Invalid API Key ???")
        messagebox.showerror("Invalid PagerDuty API Keys", "Unable to Retrieve groups, Check API Key")
        sys.exit()

    json_data = json.loads(response.text)
    global pb #pb represents the variable for a ProgressBar to denote migration is happening
    if 'teams' in json_data and len(json_data['teams']) > 0:
        for idx, team in enumerate(json_data['teams']):
            idx = idx + 1
            #Display each team in the table, along with the values specified below
            tv.insert(parent='', index=idx, iid=idx, values=(team['name'], team['id'], team['description'], team))
        style = ttk.Style()
        style.theme_use("default")
        style.map("Treeview")

        #On clicking start transfer you start the migration, for selected groups - if no group is selected it will migrate all users
        Button(ws, text="Start Transfer", command=lambda: [threading.Thread(target=show_selected).start(),pb.start()]).pack()
        pb = ttk.Progressbar(
                ws,
                orient='horizontal',
                mode='indeterminate',
                length=280
        )
        pb.pack()
        createlogArea()
    else:
        #if no teams were retrieved from PagerDuty, that is, if PD has no teams, then just migrate users from PD
        Button(ws, text="No teams - Click to just migrate users", command=lambda: [threading.Thread(target=getUsersFromPD).start(),pb.start()]).pack()
        pb = ttk.Progressbar(
                ws,
                orient='horizontal',
                mode='indeterminate',
                length=280
        )
        pb.pack()
        createlogArea()


#MAIN UI LOOP
#IN THIS PROGRAM/CODE/COMMENTS THE WORDS "Groups"/"Teams" AND "Users"/"Members"
#MAYBE USED INTERCHANGEABLY - THEY MEAN THE SAME RESPECTIVELY
#PD REPRESENTS PAGERDUTY AND AO REPRESENTS ALERTOPS
ws = Tk()
ws.title('PagerDuty to AlertOps Migrator Utility')
ws.geometry('700x250')
Label(ws, text = "Enter PagerDuty API Key").pack()
entry= Entry(ws,width= 40)
entry.focus_set()
entry.pack()
Label(ws, text = "Enter AlertOps API Key").pack()
entry2= Entry(ws, width= 40)
entry2.pack()
ttk.Button(ws, text= "Retrieve Teams and Start Migration",width= 40, command= showTable).pack(pady=20)
ws.mainloop()
