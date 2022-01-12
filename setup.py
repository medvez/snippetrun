from setuptools import setup

setup(
      name='snippetrun',
      version='2.3',
      author='Sergey Anikin',
      author_email='spa.in.spa@gmail.com',
      packages=['snippetrun'],
      scripts=['snippetrun/bin/sr_script.py'],
      package_data={'snippetrun': ['data/devices.txt', 'data/snippet.txt']},
      url='https://github.com/medvez/snippetrun',
      license='LICENSE.txt',
      description='Script which runs commands through SSH',
      long_description=open('README.md').read(),
      install_requires=['paramiko==2.8.0']
      )
