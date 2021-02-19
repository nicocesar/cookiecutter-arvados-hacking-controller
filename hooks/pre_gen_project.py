import re
import sys


CLUSTER_UUID_REGEX = r'^[a-zA-Z][a-zA-Z0-9]{4}$'

cluster_uuid = '{{ cookiecutter.cluster_uuid }}'

if not re.match(CLUSTER_UUID_REGEX, cluster_uuid):
    print('ERROR: %s is not a valid cluster name. Must start with a letter and have exactly 5 alphanumeric characters' % cluster_uuid)

    # exits with status 1 to indicate failure
    sys.exit(1)
