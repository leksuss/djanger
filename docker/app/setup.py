import re
import shlex
import subprocess

from lang import lang

lg = 'en'

def run_command(command):
    process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
    while True:
        output = process.stdout.readline()
        if process.poll() is not None:
            break
        if output:
            print (output.strip())
    rc = process.poll()
    return rc

def ask_value(is_valid, message, err_message):
    value = input(message)
    while not is_valid(value):
        print(err_message)
        value = input(message)
    return value

def is_valid(name):
    if re.match('^[a-z_]{1}[a-z_0-9]+$', name, re.IGNORECASE):
        return True
    return False

def from_env_file(filename):
    data = {}
    with open(filename, 'r') as f:
        for line in f.readlines():
            k, _, v = line.strip().partition('=')
            data[k.strip()] = v.strip().strip('"').strip("'")
    return data

def to_env_file(filename, data):
    lines = [f'{k}="{v}"' for k, v in data.items()]
    with open(filename, 'w') as f:
        f.write('\n'.join(lines))
    return data


project_name = ask_value(is_valid,
                         lang[lg]['project_name_msg'],
                         lang[lg]['project_name_err_msg']
                         )

db_name = ask_value(is_valid,
                         lang[lg]['db_name_msg'],
                         lang[lg]['db_name_err_msg']
                         )

db_user = ask_value(is_valid,
                         lang[lg]['db_user_msg'],
                         lang[lg]['db_user_err_msg']
                         )

db_password = ask_value(lambda x: True,
                         lang[lg]['db_passwd_msg'],
                         lang[lg]['db_passwd_err_msg']
                         )


docker_env = from_env_file('../../.env')
docker_env['PROJECT_NAME'] = project_name

project_dir = '../../src/' + project_name
run_command('mkdir ' + project_dir)
to_env_file(project_dir + '/.env', docker_env)
