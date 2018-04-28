from setuptools import setup
from os.path import join

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='listb',
      version='0.0',
      description='Tools for listb and MathSciNet',
      long_description=readme(),
      #url='https://github.com/tim6her/listb',
      author='Tim B. Herbstrith',
      license='MIT',
      packages=['listb'],
      scripts=[join('scripts', 'mrtools.py'),
               join('scripts', 'pybibtools.py')],
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=False)
