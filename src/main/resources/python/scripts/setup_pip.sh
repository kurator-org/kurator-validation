wget https://bootstrap.pypa.io/get-pip.py
python get-pip.py --root=${bamboo.build.working.directory}/tmp --ignore-installed
export PATH=${bamboo.build.working.directory}/tmp/usr/local/bin:$PATH
export PYTHONPATH=${bamboo.build.working.directory}/tmp/usr/local/lib/python2.7/dist-packages:$PYTHONPATH
pip install --root=${bamboo.build.working.directory}/tmp --ignore-installed virtualenv
virtualenv virtual_tmp
cd virtual_tmp
. bin/activate