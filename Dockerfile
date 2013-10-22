FROM boxcar/raring
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
ENV CONTENT_API_ROOT marquee.by/content/
ENV STATIC_URL /static/
ENV LIB_CDN_ROOT marquee-cdn.net/
ENV CACHE_SOFT_EXPIRY 10
