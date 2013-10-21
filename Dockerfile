FROM boxcar/raring
ADD . /srv/runtime
RUN apt-get update
RUN apt-get install -y python-pip
RUN apt-get install -y nodejs
RUN apt-get install -y npm
RUN pip install -r /srv/runtime/requirements.txt
RUN npm install /srv/runtime/package.json
