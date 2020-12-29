from setuptools import find_packages, setup

setup (
  name = 'chatbot',
  version='1.0.0',
  packages=find_packages(),
  include_package_data = True,
  zip_safe=False,
  install_requires = [
    'flask',
    'SocketIO',
    'flask_socketio',
    'setuptools',
    'spacy',
    'python-dateutil',
    'experta',
    'beautifulsoup4'
  ],
)