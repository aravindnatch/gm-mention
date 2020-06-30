from flask import Flask, request
import requests 
import json
import sqlite3

app = Flask(__name__)

#user variables
accesstoken = "YOUR_APPLICATION_TOKEN"
groupid = "YOUR_GROUP_ID"
botid = "YOUR_GROUP_BOT_ID"

headers = {
    'content-type': 'application/json',
    'x-access-token': accesstoken
}

@app.route('/', methods=['GET', 'POST'])
def welcome():
    return ("@aravindnatch gm-mention-server:1.0.0")

@app.route('/everyone', methods=['GET', 'POST'])
def gmAll():
    data = request.get_json()
    data['text'] = data['text'].strip()
    message = data['text'].split()
    count = 0
    send = None

    if data['group_id'] != groupid:
        return("mismatched group ids")

    if data['sender_type']=='user':
        if message[0][0:1] == '!':
            conn = sqlite3.connect('mention.db')
            c = conn.cursor()

            if message[0] == "!create" and message[1][0:1] == "@":
                tagname = message[1][1:]
                for row in c.execute(f"SELECT * FROM grouptag WHERE name = ?", (tagname,)):
                    if row[0] == message[1][1:]:
                        send = f"@{tagname} already exists"
                    break
                else:
                    count = 0
                    try:
                        for x in data['attachments'][0]['user_ids']:
                            c.execute("INSERT INTO grouptag (name,user_id) VALUES (?,?)", (tagname,x))
                            conn.commit()
                            count+=1
                        if '@myself' in data['text']:
                            c.execute("INSERT INTO grouptag (name,user_id) VALUES (?,?)", (tagname,data['user_id']))
                            conn.commit()
                            count+=1
                        send = f"created @{tagname} with {count} members"
                    except IndexError:
                        if '@myself' in data['text']:
                            c.execute("INSERT INTO grouptag (name,user_id) VALUES (?,?)", (tagname,data['user_id']))
                            conn.commit()
                            send = f"added 1 member to @{tagname}"
                        else:
                            send = "incorrect usage: use '!help' for a list of commands"
                                
            elif message[0] == "!delete" and message[1][0:1] == "@":
                tagname = message[1][1:]
                for row in c.execute(f"SELECT * FROM grouptag WHERE name = ?", (tagname,)):
                    if row[0] == tagname:
                        c.execute("DELETE FROM grouptag WHERE name = ?", (tagname,))
                        conn.commit()
                        send = f"deleted @{tagname}"
                    break
                else:
                    send = f"@{tagname} does not exist"

            elif (message[0] == "!add" or message[0] == "!remove") and message[1][0:1] == "@":
                flag = True
                tagname = str(message[1][1:])
                count = 0

                try:
                    for x in data['attachments'][0]['user_ids']:
                        for row in c.execute("SELECT * FROM grouptag WHERE name = ? and user_id = ?", (tagname,x)):
                            flag = False
                    if '@myself' in data['text']:
                        for row in c.execute("SELECT * FROM grouptag WHERE name = ? and user_id = ?", (tagname,data['user_id'])):
                            flag = False
                except IndexError:
                    if '@myself' in data['text']:
                        for row in c.execute("SELECT * FROM grouptag WHERE name = ? and user_id = ?", (tagname,data['user_id'])):
                            flag = False
                    else:
                        send = "incorrect usage: use '!help' for a list of commands"
                
                if message[0] == "!add":
                    if flag:
                        tagname = str(message[1][1:])
                        try:
                            for x in data['attachments'][0]['user_ids']:
                                c.execute("INSERT INTO grouptag (name,user_id) VALUES (?,?)", (tagname,x))
                                conn.commit()
                                count+=1
                            if '@myself' in data['text']:
                                c.execute("INSERT INTO grouptag (name,user_id) VALUES (?,?)", (tagname,data['user_id']))
                                conn.commit()
                                count+=1
                            send = f"added {count} member(s) to @{tagname}"
                        except IndexError:
                            if '@myself' in data['text']:
                                c.execute("INSERT INTO grouptag (name,user_id) VALUES (?,?)", (tagname,data['user_id']))
                                conn.commit()
                                send = f"added 1 member to @{tagname}"
                            else:
                                send = "incorrect usage: use '!help' for a list of commands"
                    else:
                        send = f"tagged member(s) already in @{tagname}"
                else:
                    if not flag:
                        tagname = str(message[1][1:])
                        try:
                            for x in data['attachments'][0]['user_ids']:
                                c.execute("DELETE FROM grouptag WHERE user_id = ? and name = ?", (x,tagname))
                                conn.commit()
                                send = f"deleted @{tagname}"
                                count+=1
                            if '@myself' in data['text']:
                                c.execute("DELETE FROM grouptag WHERE user_id = ? and name = ?", (data['user_id'],tagname))
                                conn.commit()
                                count+=1
                            send = f"removed {count} member(s) from @{tagname}"
                        except IndexError:
                            if '@myself' in data['text']:
                                c.execute("DELETE FROM grouptag WHERE user_id = ? and name = ?", (data['user_id'],tagname))
                                conn.commit()
                                send = f"removed 1 member from @{tagname}"
                            else:
                                send = "incorrect usage: use '!help' for a list of commands"
                    else:
                        send = f"tagged member(s) not in @{tagname} or group does not exist"

            elif message[0] == "!list":
                names = set()
                for row in c.execute("SELECT * FROM grouptag"):
                    names.add(row[0])
                if names:
                    nameList = list(names)
                    for x in range(len(nameList)):
                        nameList[x] = "@" + nameList[x]
                    send = "current taggable groups: " + ', '.join(nameList)
                else:
                    send = "no taggable groups"

            elif message[0] == "!help":
                send = "view documentation at https://github.com/aravindnatch/gm-mention"
            elif message[0] == "!members":
                try:
                    conn = sqlite3.connect('mention.db')
                    c = conn.cursor()

                    idList = []
                    for x in message:
                        if x[0:1] == "@":
                            findName = x[1:]
                            break

                    for row in c.execute("SELECT * FROM grouptag WHERE name = ?", (findName,)):
                        idList.append(int(row[1]))

                    getGroups = requests.get('https://api.groupme.com/v3/groups/' + data['group_id'], headers=headers)
                    groups = json.loads(getGroups.content)

                    compareList=[]
                    nameList=[]
                    for x in groups['response']['members']:
                        compareList.append(x['user_id'])
                        nameList.append(x['nickname'])

                    matchedNames = []
                    for x in range(len(compareList)):
                        if int(compareList[x]) in idList:
                            matchedNames.append(nameList[x])

                    if matchedNames == []:
                        send = "group does not exist"
                    else:
                        send = "members: " + ', '.join(matchedNames)
                except:
                    send = "invalid syntax"
            else:
                send = "incorrect usage: use '!help' for a list of commands"
            c.close()
        elif ('@all ' in data['text']) or (message[-1] == '@all'):
            getGroups = requests.get('https://api.groupme.com/v3/groups/' + data['group_id'], headers=headers)
            groups = json.loads(getGroups.content)

            idList=[]
            for x in groups['response']['members']:
                idList.append(x['user_id'])

            loci=[[] for i in range(len(idList))]
            for i in range(len(idList)):
                for j in range(2):
                    loci[i].append(0*4)

            params = {"bot_id": botid,"text": data['text'],"attachments": [{'type': 'mentions','loci': loci, 'user_ids': idList}]}
            create = requests.post('https://api.groupme.com/v3/bots/post',json=params)
        elif ('@' in data['text']):
            conn = sqlite3.connect('mention.db')
            c = conn.cursor()

            idList = []
            for x in message:
                if x[0:1] == "@":
                    findName = x[1:]
                    break

            for row in c.execute("SELECT * FROM grouptag WHERE name = ?", (findName,)):
                idList.append(int(row[1]))

            loci=[[] for i in range(len(idList))]
            bold = len(str(message[0])[1:]) + 1
            for i in range(len(idList)):
                for j in range(2):
                    loci[i].append(0*bold)
            params = {"bot_id": botid,"text": data['text'],"attachments": [{'type': 'mentions','loci': loci, 'user_ids': idList}]}
            create = requests.post('https://api.groupme.com/v3/bots/post',json=params)
            c.close()
        if send != None:
            params = {"bot_id":botid,"text":send}
            create = requests.post('https://api.groupme.com/v3/bots/post', headers=headers, params=params)
            return("message received")

    return("message received!")