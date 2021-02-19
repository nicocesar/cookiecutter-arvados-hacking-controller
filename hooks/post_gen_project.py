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


##
