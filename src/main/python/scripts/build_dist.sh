# install pip in a temporary directory
wget https://bootstrap.pypa.io/get-pip.py
python get-pip.py --root=${bamboo.build.working.directory}/tmp --ignore-installed
export PATH=${bamboo.build.working.directory}/tmp/usr/local/bin:$PATH
export PYTHONPATH=${bamboo.build.working.directory}/tmp/usr/local/lib/python2.7/dist-packages:$PYTHONPATH

# install and activate a virtualenv environment into which wheel can be installed via pip
pip install --root=${bamboo.build.working.directory}/tmp --ignore-installed virtualenv
virtualenv virtual_tmp
. virtual_tmp/bin/activate

# install the wheel package
pip install wheel

# build a wheel distribution of kurator-validator python code
cd src/main/python
python setup.py bdist_wheel
