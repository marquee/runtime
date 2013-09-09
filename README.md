# Marquee Runtime



## Setup

1. Clone the boilerplate template and install dev dependencies:

   `$ git clone git@github.com:marquee/runtime.git <project_name>`
   `$ cd <project_name>`

   *(If it’s a pre-existing project, clone from the project repo instead.)*

2. Install the various requirements:

   `$ mkvirtualenv <project_name>`
   `$ pip install -r requirements.txt`
   `$ npm install`

3. Re-initialize the repo and copy the .env templates:

   `$ cake init`

   *(If this is a pre-existing project, use `init:env` instead.)*

4. Add additional remotes (if necessary)

   `$ git add remote origin git@git.droptype.com:<project_name>.git`
   `$ git add remote heroku git@heroku.com:<project_name>.git`

5. Fill out the environment variables:

   In `.env`:

   * `CONTENT_API_TOKEN` - A read-only ApplicationToken issued by Marquee.
   * `PUBLICATION_NAME` - Arbitrary project name
   * `PUBLICATION_SHORT_NAME` - The short name, used to prefix the asset uploads

   In `.env-development`:

   * `AWS_ACCESS_KEY_ID`
   * `AWS_SECRET_ACCESS_KEY`

   (They are in separate files to keep credentials that have write access
   segregated. The `.env` file MUST NOT ever contain API tokens or Access
   Keys or whatever that have write privileges.)



## Running the project

First, make sure you are in the virtualenv: `$ workon <project_name>`

To run the project in debug mode, with the auto reloader, use
`$ python run.py debug`.

To run the project as if it is on Heroku, use `$ foreman start`. The project
also supports caching using redis. To use this locally, start redis and set
the `REDIS_URL` in `.env`.



## Deploying the project

(Assuming [Heroku](https://github.com/droptype/marquee/wiki/Heroku-Setup))

If this is the first time the app is being deployed, you need to set
certain environment variables using `$ heroku config:set`
They can be set (almost) all at once:

    $ heroku config:set CACHE_SOFT_EXPIRY=10 CONTENT_API_TOKEN=<read_only_token> CONTENT_API_ROOT=marquee.by/content/ DEBUG=False ENVIRONMENT=production PUBLICATION_NAME="<publication name>" SECRET_KEY=<secret_key> PUBLICATION_SHORT_NAME=<short_name>

To deploy the code, just `$ git push heroku master`. You’ll also want
to run `$ cake deploy:static` if you made changes to the static assets.



## Static Files

Static assets require CoffeeScript and Compass, as usual. The build process is
managed by `cake`. The source files go into `static_source/` and come out in
`static/`.


### `$ cake <command>`

* `flush:static` - clear the `static/` directory
* `build` - flush static and rebuild all static files
    * `build:scripts` - compile just the scripts
    * `build:styles` - compile just the styles
    * `build:other` - copy non-coffee/-sass files
* `watch` - flush static and start the CoffeeScript and Compass watchers

   Note: there is nothing running that updates images when they 
   change, so you’ll have to run `$ cake build:other` to update
   those.

* `deploy:static` - build and upload the static files to S3

   If you’ve set up the project as a Heroku app, this command will
   also update the `STATIC_URL` env variable of the app and restart
   the server, using the `heroku config:set` command.


### Serving

In development, static assets for offsite publications are served locally by
the Flask app. In production, the assets are served at `http://cdn.mrqe.co`,
via CloudFront. The assets are stored in the `cdn.mrqe.co` S3 bucket, with the
keys prefixed by `<short_name>/<hash>`, where `<hash>` is the first 18
characters of a `SHA-1` hash of the asset contents.

To refer to a static asset in the templates, use
`{{ static_url('filename.jpg') }}`. This will use the appropriate `STATIC_URL`.

