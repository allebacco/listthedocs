from setuptools import setup, find_packages

setup(
    name='listthedocs',
    version='2.0.0',
    description='List your documentations',
    author='Alessandro Bacchini',
    author_email='allebacco@gmail.com',
    url='https://github.com/allebacco/listthedocs',
    packages=find_packages(),
    install_requires=[
        'Flask',
        'natsort',
        'requests',
        'attrs',
        'python-dateutil',
        'Flask-SQLAlchemy',
    ],
    tests_require=[
        'pytest'
    ]
)
