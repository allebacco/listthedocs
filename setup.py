from setuptools import setup, find_packages

setup(
    name='listthedocs',
    version='1.0.0',
    description='List your documentations',
    author='Alessandro Bacchini',
    author_email='allebacco@gmail.com',
    url='https://github.com/allebacco/listthedocs',
    packages=find_packages(),
    install_requires=[
        'Flask',
        'natsort',
    ],
    tests_require=[
        'pytest'
    ]
)
