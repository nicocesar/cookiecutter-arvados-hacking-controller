import re
import sys

CLUSTER_UUID_REGEX = r'^[a-zA-Z][a-zA-Z0-9]{4}$'
update_etc_hosts = '{{ cookiecutter.update_etc_hosts}}' == 'yes'

if not re.match(CLUSTER_UUID_REGEX, '{{ cookiecutter.cluster_uuid }}'):
  print('ERROR: {{ cookiecutter.cluster_uuid }} is not a valid cluster name. Must start with a letter and have exactly 5 alphanumeric characters')
  # exits with status 1 to indicate failure
  sys.exit(1)


if update_etc_hosts:
  # check if there is not conflicting ip+cluster_uuids in /etc/hosts.
  # 1. filter all comments and bank lies then
  # 2. filter all lines from that start with the IP,
  # 3. filter out the ones that have the cluster_id
  #   if is empty, we're fine. Otherwise complain.
  with open('/etc/hosts') as f:
    etc_hosts = [x.rstrip() for x in f if not x.startswith("#") and not x=='\n']
    with_that_ip =[x for x in etc_hosts if x.startswith('{{ cookiecutter.ip_address }}')]
    conflicting_lines = [x for x in with_that_ip if '{{ cookiecutter.cluster_uuid }}' not in x]
    if len(conflicting_lines) > 0:
      print("\nERROR: the following lines have conflics with {{ cookiecutter.ip_address }} and {{ cookiecutter.cluster_uuid }}\n")
      for line in conflicting_lines:
          print(line+"\n")
      print("\n")
      sys.exit(1)