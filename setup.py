from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='listthedocs',
    version='1.0.4',
    author='Alessandro Bacchini',
    author_email='allebacco@gmail.com',
    description='List your documentations',
    long_description=long_description,
    long_description_content_type="text/markdown",
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
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Topic :: Documentation",
        "Topic :: Software Development :: Documentation",
    ],
    python_requires='>=3.5',
)
