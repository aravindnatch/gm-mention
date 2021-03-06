# GroupMe Mention
Groupme Mention is a bot framework that allows users to create custom groups to tag multiple people at once. This project was built with Python using Flask.

## Getting Started
You will need to retrieve a GroupMe application token, your group id, and that group's bot id. **Be sure to set your GroupMe callback url to the url that your server will be running on (ex. public.ip:3106 or xxx.duckdns.org:3106)**

1. Install dependencies
```
pip3 install -r requirements.txt
```
2. Set Variables in gm-mention.py
```
#user variables
accesstoken = "YOUR_APPLICATION_TOKEN"
groupid = "YOUR_GROUP_ID"
botid = "YOUR_GROUP_BOT_ID"
```
3. Run Application
```
flask run --host=0.0.0.0 --port=3106
```

## How to Use

### Commands
Create a Group
```
!create @testgroup @person1 @person2 @person3
```

Delete a Group
```
!delete @testgroup
```

Add Members to a Group
```
!add @testgroup @member1 @member2
```

Remove Members From a Group
```
!remove @testgroup @member1 @member2
```

List All Taggable Groups
```
!list
```

List Members in a Group
```
!members @testgroup
```

Any Member Action to Yourself
```
... @myself
```

### Invocation

Specific Group
```
Any User: @testgroup
Bot Response: @testgroup <- Bold and Notifys users in tagged group
```

Everyone
```
Any User: @all
Bot Response: @all <- Bold and Notifys everyone in groupchat
