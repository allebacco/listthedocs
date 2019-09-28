from setuptools import setup, find_packages

setup(
    name='listthedocs',
    version='1.0.4',
    description='List your documentations',
    author='Alessandro Bacchini',
    author_email='allebacco@gmail.com',
    url='https://github.com/allebacco/listthedocs',
    packages=find_packages(),
    package_data={'listthedocs': [
            'listthedocs/templates/*.*',
            'listthedocs/static/styles/*.*',
        ]
    },
    include_package_data=True,
    install_requires=[
        'natsort',
        'requests',
        'attrs',
        'python-dateutil',
        'Flask-SQLAlchemy',
        'Flask',
    ],
    tests_require=[
        'pytest'
    ]
)
