from setuptools import setup
from os.path import join

def readme():
    with open('README.rst') as f:
        return f.read()

def requirements():
    with open('requirements.txt') as f:
        return f.read()

setup(name='listb',
      version='0.0',
      description='Tools for listb and MathSciNet',
      long_description=readme(),
      #url='https://github.com/tim6her/discogs_finder',
      author='Tim B. Herbstrith',
      license='MIT',
      packages=['listb'],
      install_requires=requirements(),
      scripts=[join('scripts', 'mrtools'),
               join('scripts', 'pybibtools')],
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=False)
