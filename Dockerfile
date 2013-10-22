FROM ubuntu:quantal
ADD . /srv/runtime
RUN apt-get update
RUN apt-get install -y python-pip
RUN apt-get install -y nodejs
RUN apt-get install -y npm
RUN apt-get install -y ruby
RUN apt-get install -y rubygems
RUN gem install compass
RUN pip install -r /srv/runtime/requirements.txt
RUN npm install /srv/runtime/package.json
