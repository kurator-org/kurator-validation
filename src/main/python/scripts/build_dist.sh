TMPDIR=${bamboo.build.working.directory}/tmp

# install pip in a temporary directory
wget https://bootstrap.pypa.io/get-pip.py
python get-pip.py --root=$TMPDIR --ignore-installed
export PATH=$TMPDIR/usr/local/bin:$PATH
export PYTHONPATH=$TMPDIR/usr/local/lib/python2.7/dist-packages:$PYTHONPATH

# install and activate a virtualenv environment into which wheel can be installed via pip
pip install --root=$TMPDIR --ignore-installed virtualenv
virtualenv virtual_tmp
. virtual_tmp/bin/activate

# install the wheel package
pip install wheel

# build a wheel distribution of kurator-validator python code
cd src/main/python
python setup.py bdist_wheel