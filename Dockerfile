FROM python:3-alpine

ADD ./listthedocs/ ./listthedocs/
ADD ./MANIFEST.in ./MANIFEST.in
ADD ./setup.py ./setup.py

EXPOSE 5000

CMD [ "python", "runserver.py" ]
