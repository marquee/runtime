# Marquee Runtime

## Getting Started

The Marquee Runtime comes with it's own development environment that runs on [Vagrant](http://vagrantup.com) and is provisioned by [Ansible](http://ansibleworks.com). Because Ansible support in Vagrant is still under heavy development, we will need to install both [Vagrant](https://github.com/mitchellh/vagrant) and [Ansible](https://github.com/ansible/ansible) from source.

You'll first want to uninstall any current installations of Vagrant by running through the uninstall package in the [official binaries](http://downloads.vagrantup.com/).

If you don't have rubygems or bundler installed, you need them.

```
→ brew install rubygems
→ gem install bundler
```

Then build and install Vagrant

```
→ git clone https://github.com/mitchellh/vagrant.git
→ cd vagrant
→ bundle install
→ rake install
```

You can install Ansible using pip, but modules are still in heavy flux and keeping different versions of it in virtualenvs is more trouble than it's worth. Just install it from it's pretty stable source, and you'll be fine. Homebrewed it for simplicity.

```
# Install from source
→ brew install ansible --HEAD

# Keep up-to-date
→ brew upgrade ansible --HEAD
```

The virtual machine used for the development environment will use private networking and assign itself the IP address `10.10.10.2`. To make your life easier, you should ignore host checking when ssh'ing to it; otherwise, you're going to have to delete lines in `~/.ssh/known_hosts` every time you rebuild the box.

Add the following to `~/.ssh/config` to save yourself some time:

```
Host 10.10.10.2
  StrictHostKeyChecking no
  UserKnownHostsFile /dev/null
```

You're now good to go. Clone this repository into a *New Project* and then fire up vagrant to get to work.

```
→ git clone https://github.com/marquee/runtime.git <project_name>
→ cd <project_name>
→ vagrant up
```

Vagrant will run through setting up an [Ubuntu Server 13.04 (Raring) Cloud Image](http://cloud-images.ubuntu.com/) virtual machine,  install requirements, and set up your development environment. 

You can access the development environment simply by running `vagrant ssh`. Defaults are defined in the [vagrant group_vars](https://github.com/marquee/runtime/tree/master/provisioning/group_vars/vagrant). Highlights below:

- The runtime located is in your home directory at `/home/vagrant/runtime`. You are logged into this directory when you SSH into the machine. The root directory of the repository on the host machine is synced here, so you can work locally and changes will automatically appear within the development environment and reload watching scripts appropriately.

- A Python virtual environment named `runtime` is created and into it all dependencies of the application installed. It is activated for you when you log into the virtual machine.

## Configuration

First, make sure the following settings have been configured in your `.env` file:

- `CONTENT_API_TOKEN`
- `PUBLICATION_NAME`
- `PUBLICATION_SHORT_NAME`

If you're going to be deploying this application publicly, you'll also want to hook up your AWS credentials so that static files can be handled by S3. These settings can be found in `.env-development`.

## Running the Runtime

Once your `.env` and `.env-development` files are filled out, you'll be able to fire up runtime. To do so, we'll first SSH into the box, then run the `runserver` command.

```
→ vagrant ssh
# Stuff happens
→ runserver
```

This will make the runtime accessible at [http://10.10.10.2:5000](http://10.10.10.2:5000).



## Deploying the project

(Assuming [Heroku](https://github.com/droptype/marquee/wiki/Heroku-Setup))

If this is the first time the app is being deployed, you need to set
certain environment variables using `$ heroku config:set`
They can be set (almost) all at once:

    $ heroku config:set CACHE_SOFT_EXPIRY=10 \
    CONTENT_API_TOKEN=<read_only_token> \
    CONTENT_API_ROOT=marquee.by/content/ \
    DEBUG=False ENVIRONMENT=production \
    PUBLICATION_NAME="<publication name>" \
    SECRET_KEY=<secret_key> \
    PUBLICATION_SHORT_NAME=<short_name>
    
You can also use [this python script](https://gist.github.com/alexcabrera/63b993a604cdb5410ce8) to configure Heroku for you. 

Fire and forget one-liner:

```
curl -L http://mrqe.co/1cKkLEV | python
```

To deploy the code, just `git push heroku master`. You’ll also want
to run `cake deploy:static` if you made changes to the static assets.



## Static Files

Static assets require CoffeeScript and Compass, as usual. The build process is
managed by `cake`. The source files go into `static_source/` and come out in
`static/`.

### Libraries

Front-end libraries are available on a CDN (CloudFront). The preferred way to
use them in a template is using the `{% cdn … %}` template tag. This tag will
automatically generate the appropriate HTML tag for the library, using the
`LIB_CDN_ROOT` environment variable. It also will choose the minified or
development version, depending on the environment, and will point to the
gzipped version if the client accepts it.

To use, simply include the tag `{% cdn 'library-x.y.z.type' %}` where the
library needs to be included. Multiple libraries can be provided, comma-
separated, `{% cdn 'library1-x.y.z.js','library2-x.y.z.js' %}`. The name of
the library looks like a file name, but is actually a pattern:

    <library_module>[.<library_submodule>]-<major>.<minor>.<patch>.<type>

The tag parses this pattern and uses it to construct the necessary HTML tags.

Example:

    {% cdn 'zepto-1.0.0.js' %}

will yield one of the following possible tags, depending on the environment
and request:

    <script src="//marquee-cdn.net/zepto-1.0.0.js"></script>
    <script src="//marquee-cdn.net/zepto-1.0.0.js.gz"></script>
    <script src="//marquee-cdn.net/zepto-1.0.0-min.js"></script>
    <script src="//marquee-cdn.net/zepto-1.0.0-min.js.gz"></script>

While a usage like

    {% cdn 'formwork-0.1.2.css' %}

will yeild:

    <link rel="stylesheet" type="text/css" href="//marquee-cdn.net/formwork-0.1.2.css">
    <link rel="stylesheet" type="text/css" href="//marquee-cdn.net/formwork-0.1.2.css.gz">
    <link rel="stylesheet" type="text/css" href="//marquee-cdn.net/formwork-0.1.2-min.css">
    <link rel="stylesheet" type="text/css" href="//marquee-cdn.net/formwork-0.1.2-min.css.gz">

See the [Marquee CDN repo](https://github.com/marquee/marquee-cdn) for a list
of all the libraries available.

*Note: the tag is not aware of the library manifest, so it will generate the
HTML tags even if the library does not exist.*


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

## Troubleshooting

### SSH Error during *Getting Facts* stage of provisioning

When bringing up the runtime environment with `vagrant up` for the first time, you may see the following message when Ansible attempts to begin provisioning:

```
GATHERING FACTS ***************************************************************
fatal: [10.10.10.2] => SSH encountered an unknown error during the 
connection. We recommend you re-run the command using -vvvv, which will 
enable SSH debugging output to help diagnose the issue
```

Sometime its takes a little bit for the SSH server on the Vagrant box to fire up. Simply running `vagrant provision` to start the provisioning process over again should make it go away.

