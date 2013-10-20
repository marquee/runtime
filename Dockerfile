FROM boxcar/raring
RUN apt-get update
RUN apt-get install -y python-pip
RUN pip install flask
ADD . /srv/runtime
RUN ls /srv/runtime
