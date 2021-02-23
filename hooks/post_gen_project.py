import os
import subprocess

TARGET = os.getcwd()

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
subprocess.check_call(["git","clone", "{{cookiecutter.arvados_repo}}","-b","{{cookiecutter.arvados_branch}}"])


## TODO: update configs/build/LAST_BUILD_INFO with git info from ./arvados
## TODO: generate certificates + CA ?
### CA:

#openssl genrsa -des3 -out myCA.key 2048
#openssl req -x509 -new -nodes -key myCA.key -sha256 -days 1825 -out myCA.pem

### DOMAIN
#openssl genrsa -out $DOMAIN.key 2048
#openssl req -new -key $DOMAIN.key -out $DOMAIN.csr

#cat > $DOMAIN.ext << EOF
#authorityKeyIdentifier=keyid,issuer
#basicConstraints=CA:FALSE
#keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment
#subjectAltName = @alt_names
#[alt_names]
#DNS.1 = $DOMAIN
#EOF

#openssl x509 -req -in $DOMAIN.csr -CA ../myCA.pem -CAkey ../myCA.key -CAcreateserial \
#-out $DOMAIN.crt -days 825 -sha256 -extfile $DOMAIN.ext
