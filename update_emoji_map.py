import requests

response = requests.get('https://raw.githubusercontent.com/mattermost/platform/master/webapp/utils/emoji.json').json()

with open('mattersend.py', 'r') as f:
    mattersend_py = f.readlines()

updated_mattersend_py = []

in_block = False
for line in mattersend_py:
    if not in_block:
        updated_mattersend_py.append(line)

        if line == 'emoji_to_code = {\n':
            in_block = True

            for icondata in response:
                name = icondata[1]['name']
                code = icondata[1].get('unicode', name)
                updated_mattersend_py.append("    '{0}': '{1}',\n".format(name, code))

    elif line == '}\n':
        updated_mattersend_py.append(line)
        in_block = False

with open('mattersend.py', 'w') as f:
    f.write(''.join(updated_mattersend_py))
