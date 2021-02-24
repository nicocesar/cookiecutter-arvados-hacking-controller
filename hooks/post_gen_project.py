import os
import subprocess
import random

TARGET = os.getcwd()

## important files

CA_KEY = '{{cookiecutter.default_configs_dir}}/ssl/{{cookiecutter.cluster_uuid}}.{{cookiecutter.domain}}-CA.key'
CA_CRT = '{{cookiecutter.default_configs_dir}}/ssl/{{cookiecutter.cluster_uuid}}.{{cookiecutter.domain}}-CA.crt'

DOMAIN_KEY = '{{cookiecutter.default_configs_dir}}/ssl/%s.{{cookiecutter.cluster_uuid}}.{{cookiecutter.domain}}.key'
DOMAIN_CERT = '{{cookiecutter.default_configs_dir}}/ssl/%s.{{cookiecutter.cluster_uuid}}.{{cookiecutter.domain}}.crt'
DOMAIN_REQ = '{{cookiecutter.default_configs_dir}}/ssl/%s.{{cookiecutter.cluster_uuid}}.{{cookiecutter.domain}}.csr'

## replace $((INSTALL)) after cloning with current directory
# this is needed because cookiecutter doesn't have a way to express this 
# https://github.com/cookiecutter/cookiecutter/issues/955#issuecomment-444864537
for root, dirs, files in os.walk(TARGET):
    for filename in files:
        # read file content
        with open(os.path.join(root, filename)) as f:
            content = f.read()
        # replace tag by install path
        content = content.replace('$((INSTALL))', TARGET)
        # replace file content
        with open(os.path.join(root, filename), 'w') as f:
            f.write(content)

## clone arvados repo and check out the right branch
subprocess.check_call('git clone {{cookiecutter.arvados_repo}} -b {{cookiecutter.arvados_branch}}'.split(' '))


## TODO: update configs/build/LAST_BUILD_INFO with git info from ./arvados
## TODO: generate certificates + CA ?
### CA:

print("[ 1   ] Trying to generate certs...")
print("[ 1.1 ] Generating CA")
subprocess.check_call(['openssl', 'req', '-new', '-nodes', '-sha256', '-x509',
 '-subj', '/C=CC/ST=Arvie grep State/O=__ARVIE__/OU=arvie/CN=snakeoil-ca-{{cookiecutter.cluster_uuid}}.{{cookiecutter.domain}}',
 '-extensions', 'x509_ext',
 '-config', '{{cookiecutter.default_configs_dir}}/ssl/openssl-ca.cnf',
 '-out', CA_CRT,
 '-keyout', CA_KEY,
 '-days', '3650'],
stderr=subprocess.STDOUT)

## format [Name, CN, update_etc_host]
## controller database keep collections download workbench workbench2 ws; 
certificates = [
  ['controller','{{cookiecutter.cluster_uuid}}.{{cookiecutter.domain}}', True],
  ['database','database.{{cookiecutter.cluster_uuid}}.{{cookiecutter.domain}}', False],
  ['keep','keep.{{cookiecutter.cluster_uuid}}.{{cookiecutter.domain}}', True],
  ['collections','collections.{{cookiecutter.cluster_uuid}}.{{cookiecutter.domain}}', True],
  ['download','download.{{cookiecutter.cluster_uuid}}.{{cookiecutter.domain}}', True],
  ['workbench','workbench.{{cookiecutter.cluster_uuid}}.{{cookiecutter.domain}}', True],
  ['workbench2','workbench2.{{cookiecutter.cluster_uuid}}.{{cookiecutter.domain}}', True],
  ['ws','ws.{{cookiecutter.cluster_uuid}}.{{cookiecutter.domain}}', True],
  ]

### DOMAIN 
## csr

for name, cn, _ in certificates:
  print("[ 1.2 ] Generating cert for %s" % name)
  subprocess.check_call(['openssl', 'req', '-new', '-nodes', '-sha256',
    '-subj', '/C=CC/ST=Arvie State/O=__ARVIE__/OU=arvie/CN=%s' % cn, 
    '-out', DOMAIN_REQ % name,
    '-keyout', DOMAIN_KEY % name,
    '-extensions', 'x509_ext',
    '-config', '{{cookiecutter.default_configs_dir}}/ssl/openssl-cert.cnf',
    '-addext', 'subjectAltName=DNS:localhost,DNS:%s' % cn ],
    stderr=subprocess.STDOUT)

  ## cert
  subprocess.check_call(['openssl', 'x509', '-req', '-days', '3650',
    '-in', DOMAIN_REQ % name,
    '-out', DOMAIN_CERT % name,
    '-extensions', 'x509_ext',
    '-extfile', '{{cookiecutter.default_configs_dir}}/ssl/openssl-cert.cnf',
    '-CA',CA_CRT,
    '-CAkey', CA_KEY, 
    '-set_serial', str(random.randrange(1, 99999999))]  ,
    stderr=subprocess.STDOUT) 

## add hosts /etc/hosts
if '{{cookiecutter.update_etc_hosts}}' == 'yes':
  print("[ 2   ] Trying to update /etc/hosts...")
  p_grep = subprocess.run(['grep','-q','{{cookiecutter.cluster_uuid}}.{{cookiecutter.domain}}','/etc/hosts'], check=False)
  if p_grep.returncode == 1:
    print("[ 2.1 ] entry for {{cookiecutter.cluster_uuid}}.{{cookiecutter.domain}} in /etc/hosts is missing...")
    p_tee = subprocess.Popen('sudo tee --append /etc/hosts',
                        shell=True, stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE)
    ## dns_update is the record we'll use in /etc/hosts
    dns_update = '''
# Arvados development cluster {{cookiecutter.cluster_uuid}}.{{cookiecutter.domain}}"
127.0.0.2 %s

''' % " ".join([x[1] for x in certificates if x[2]])

    p_tee.communicate(input=bytes(dns_update,'UTF-8'))
  else:
    print("[ 2.2 ] entry for {{cookiecutter.cluster_uuid}}.{{cookiecutter.domain}} in /etc/hosts there...")
else:
  print("[ 2.3 ] Skipping update /etc/hosts")


print('''

End of the installation. To test it out: 

cd {{cookiecutter.cluster_uuid}}
DOCKER_BUILDKIT=1 code .

And there will be a dialog "Folder containes Dev Container configuration file",
click in "Reopen in container". Once the environment is up, press F5 to debug.

''')