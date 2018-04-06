from setuptools import setup

setup(
    name='Server',
    packages=['server'],
    include_package_data=True,
    install_requires=[
        'flask',
        'ConfigParser',
        'pika',
        'importlib',
        'enum'
    ],
)
