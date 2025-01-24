# open members.txt, read each line, and write to members.json

import json
import os

members_txt = os.path.join(os.path.dirname(__file__), 'members.txt')
members_json = os.path.join(os.path.dirname(__file__), 'members.json')

with open(members_txt) as f:
    usernames = f.read().splitlines()
    usernames = [username.lower() for username in usernames]
    members = {"usernames": usernames}
    with open(members_json, 'w') as f:
        json.dump(members, f)
