import re
import secrets
import shlex
import subprocess
from pathlib import Path

from lang import lang


lg = 'en'
BASE_DIR = str(Path(__file__).resolve().parents[2]) + '/'

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
    return re.match('^[a-z_]{1}[a-z_0-9]+$', name, re.IGNORECASE)

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

'''
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
db_ext_port = ask_value(lambda x: x.isdigit(),
                         lang[lg]['db_ext_port_msg'],
                         lang[lg]['db_ext_port_err_msg']
                         )
'''
project_name = 'myproj'
db_name = 'myproj'
db_user = 'myproj_user'
db_password = 'password'
db_ext_port = 5431


docker_env = from_env_file(BASE_DIR + '.env')
docker_env.update({
    'PROJECT_NAME': project_name,
    'EXT_POSTGRES_PORT': db_ext_port,  # external port to connect outside docker compose
})
to_env_file(BASE_DIR + '.env', docker_env)

project_env = {
    'POSTGRES_USER': db_user,
    'POSTGRES_PASSWORD': db_password,
    'POSTGRES_DB': db_name,
    'POSTGRES_PORT': 5432,  # default port
    'POSTGRES_HOSTNAME': 'db',  # database container name
    'SECRET_KEY': secrets.token_hex(50),  # get_random_secret_key() is insecure https://git.io/JnPEX
    'DEBUG': True,
    'ALLOWED_HOSTS': '0.0.0.0,',
    'PROJECT_NAME': project_name,
}

project_dir = BASE_DIR + 'src/' + project_name
run_command('mkdir ' + project_dir)
to_env_file(project_dir + '/.env', project_env)

# run_command('docker compose -f ../../docker-compose.yml up --abort-on-container-exit app')
run_command(f'docker compose -f {BASE_DIR}docker-compose.yml run --rm app django-admin startproject {project_name} .')
run_command(f'cp {BASE_DIR}docker/setup/settings_template.py {project_dir}/settings.py')
run_command(f'docker compose -f {BASE_DIR}docker-compose.yml run --rm app python manage.py migrate')


##todo
'''
  - сделать файл settings.py с настроенными параметрами, возможно, часть из них вынести в settings_local
  - подключить postgres (после того как настроим сеттингс), т.к. ща sqlite по дефолту
  - разобраться, в какой момент и как сделать migrate после создания проекта
  - разобраться с static и media директориями (тоже в settings), мб надо collectstatic сделать
'''