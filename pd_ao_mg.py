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

def declare_a_global_pdkey(api_key):
    global pd_api_key
    pd_api_key = api_key

def declare_a_global_aokey(api_key):
    global ao_api_key
    ao_api_key = api_key

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


def show_selected():
    t.config(state="normal")
    json_data = {}
    groupsToBeAdded = []
    uIds = []
    if not tv.selection():
        t.insert(END, "- No Groups selected - Transferring just users available \n")
        getUsersFromPD()
    else:
        for i in tv.selection():
            groupNamesSelected = tv.item(i)
            json_data = groupNamesSelected["values"][3]
            json_data = ast.literal_eval(json_data)
            addGroupstoAO(json_data)
            groupsToBeAdded.append(json_data['name'])
            ids = listMembersOfgroup(json_data,uIds)

        ids = list(list(OrderedDict.fromkeys(ids)))

        for id in ids:
            userobj = getUser(id)
            addUserToAO(userobj,groupsToBeAdded)
        t.config(state="disabled")
        pb.stop()

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

def getUser(id):
    url = f'https://api.pagerduty.com/users/{id}'
    payload={}
    headers = {
      'Authorization': 'Token token='+pd_api_key
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    json_data = json.loads(response.text)
    return json_data

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


def addUserToAO(user,groupsToBeAdded):
    url = "https://api.alertops.com/api/v2/users"


    #Formatting the name to get the first name, last name and username
    nameOriginal = user['user']['name']
    nameSplit = nameOriginal.split() #assuming a single firstname and lastname, first name will be nameSplit[0], lastname will be nameSplit][1]
    username = user['user']['email']
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


    if len(user['user']['teams']) > 0:
        addUserToGroupAO(user,username,groupsToBeAdded)




def addUserToGroupAO(user,username,groupsToBeAdded):
    teamNames = user['user']['teams']
    for team in teamNames:
        if team['summary'] in groupsToBeAdded:
            gId = getGroupIDFromAO(team)
            addUserToGID(gId,user,username,team)


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


def showTable():
    global tv
    global entry
    global entry2
    global label
    pd_api_key= entry.get()
    ao_api_key= entry2.get()
    declare_a_global_pdkey(pd_api_key)
    declare_a_global_aokey(ao_api_key)
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
    global pb
    if 'teams' in json_data and len(json_data['teams']) > 0:
        for idx, team in enumerate(json_data['teams']):
            idx = idx + 1
            tv.insert(parent='', index=idx, iid=idx, values=(team['name'], team['id'], team['description'], team))
        style = ttk.Style()
        style.theme_use("default")
        style.map("Treeview")
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
        Button(ws, text="No teams - Click to just migrate users", command=lambda: [threading.Thread(target=getUsersFromPD).start(),pb.start()]).pack()
        pb = ttk.Progressbar(
                ws,
                orient='horizontal',
                mode='indeterminate',
                length=280
        )
        pb.pack()
        createlogArea()


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
