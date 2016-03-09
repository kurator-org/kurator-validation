'''
This script builds archives (zip files) for distributing and installing the
kurator-worms python package (services, actors, and example scripts).

***** Building a source distribution ****

To build a source distribution archive run this script with the sdist argument
and find the archive (e.g. kurator_worms-0.1.tar.gz) in the dist subdirectory:

$ python setup.py sdist
 

***** Building a wheel distribution *****

To build a universal wheel distribution first install the wheel package:

$ pip install wheel

Then run this script with the bdist_wheel argument and find the wheel archive 
(e.g. kurator_worms-0.1-py2.py3-none-any.whl) in the dist directory. The wheel produced
is universal (works both with Python 2 and 3 distributions) because the universal
flag is given in the setup.cfg file.

$ python setup.py bdist_wheel


***** Installing this package *****

Either the source distribution or the wheel distribution can be installed
using pip, which will install the dependencies as well:

$ pip install kurator_worms-0.3.1-py2.py3-none-any.whl

'''

from setuptools import setup, find_packages

setup(
    name='kurator_worms',
    version='0.1',
    description='Data validation services and actors',
    author='Kurator Project',
    author_email='kurator@lists.illinois.edu',
    url='https://github.com/kurator-org/kurator-validation/tree/master/packages/kurator_worms',
    packages=find_packages(),
    install_requires=['suds-jurko'],
    license='MIT',
     classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
		'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
)