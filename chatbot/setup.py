from setuptools import setup

setup (
    name = 'chatbot',
    packages = ['chatbot'],
    include_package_data = True,
    install_requires = [ 'flask' ],
)