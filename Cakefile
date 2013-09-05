{ spawn, exec }     = require 'child_process'
util                = require 'util'
fs                  = require 'fs-extra'
AWS                 = require 'aws-sdk'
crypto              = require 'crypto'
mime                = require 'mime'
path                = require 'path'
UglifyJS            = require 'uglify-js'
walk                = require 'walk'
execSync            = require 'execSync'
 
# Configuration
PROJECT_NAME = fs.realpathSync(__filename)
PROJECT_ROOT = path.join(path.dirname(PROJECT_NAME))
 
ASSET_SOURCE   = path.join(PROJECT_ROOT, 'static_source/')
ASSET_OUTPUT   = path.join(PROJECT_ROOT, 'static/')
 
 
 
# Options
option '-q', '--quiet',         'Suppress non-error output'
option '-p', '--production',    'Compile for production'
option '-f', '--force',         'Force action'
 
REQUIRED_ENV_VARS = ['PUBLICATION_SHORT_NAME', 'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'S3_BUCKET_NAME']
ENV = null
s3 = null
 
ENV_FILE = path.join(PROJECT_ROOT, '.env')
ENV_DEVELOPMENT_FILE = path.join(PROJECT_ROOT, '.env-development')
 
loadEnvFile = (f) ->
    try
        data = fs.readFileSync(f)
    catch e
        throw new Error("You are missing a `#{ f }` file")
    data.toString().split(/\n/).forEach (line) ->
        unless line is ''
            [key, val] = line.split('=', 2)
            ENV[key] = val
 
setUpEnv = ->
    unless ENV?
        ENV = {}
        loadEnvFile(ENV_FILE)
        loadEnvFile(ENV_DEVELOPMENT_FILE)
        missing_env_vars = []
        REQUIRED_ENV_VARS.forEach (env_var) ->
            unless ENV[env_var]?.length > 0
                missing_env_vars.push(env_var)
 
        unless missing_env_vars.length is 0
            throw new Error("You are missing the following env variables: #{ missing_env_vars.join(', ') }")
 
 
 
 
 
# Helpers
 
executeCommand = (command, options, callback, errorCB) ->
    exec command.join(' '), (err, stdout, stderr) ->
        if err?
            console.log '\n\n\n', '*******************', command, 'failed!\n\n***************\n', err, stderr
            if errorCB?
                errorCB(err)
            else
                throw err
        else
            unless options.quiet
                console.log stderr
                console.log stdout
            callback?()
 
spawnCommand = (command, callback) ->
    command_name = command.shift()
    watcher = spawn(command_name, command)
    watcher.stdout.on 'data', (data) ->
        data = data.toString().trim()
        if data.length > 10
            console.log "#{ command_name }.stdout: #{ data }"
    watcher.stderr.on 'data', (data) ->
        data = data.toString().trim()
        if data.length > 10
            console.log "#{ command_name }.stderr: #{ data }"
    watcher.on 'close', (exit_code) ->
        console.log "#{ command_name } exit: #{ exit_code }"
    callback?()
 
makeCompassCommand = (command, options) ->
    compass_command = ['compass', command, '--force']
    compass_command.push('--environment')
    if options.production
        compass_command.push('production')
    else
        compass_command.push('development')
 
    compass_extra_options = [
        '--relative-assets',
        '--require',            'compass-normalize',
        '--sass-dir',           ASSET_SOURCE,
        '--css-dir',            ASSET_OUTPUT,
        '--images-dir',         ASSET_SOURCE,
        '--javascripts-dir',    ASSET_OUTPUT,
    ]
 
    python_base = execSync.exec('which python').stdout.trim().replace(path.join('bin', 'python'),'')
    extensions = ['composer'].map (ext_name) -> path.join(python_base, 'src', ext_name)
 
    extensions.forEach (ext) ->
        compass_extra_options.push('--load')
        compass_extra_options.push(ext)
 
    compass_command.push(compass_extra_options...)
    return compass_command
 
hashFiles = (file_list, callback) ->
    data_to_hash = []
    file_list.forEach (file_obj) ->
        file_obj.getContents (data) ->
            data_to_hash.push(data.toString())
            if data_to_hash.length is file_list.length
                hash = crypto.createHash('sha1')
                data_to_hash.forEach (d) -> hash.update(d)
                callback(hash.digest('hex')[...18])
 
minifyScripts = (options, callback) ->
    console.log 'Minifying scripts in place'
    asset_list = []
    walker = walk.walk(ASSET_OUTPUT)
    walker.on 'file', (root, file_stats, next) ->
        if file_stats.name.split('.').pop() is 'js'
            asset_list.push(path.join(root, file_stats.name))
        next()
    walker.on 'end', ->
        num_compressed = 0
        if asset_list.length is 0
            console.log 'No js to minify'
            callback?()
        else
            asset_list.forEach (file_path) ->
                console.log file_path
                fs.readFile file_path, (err, data) ->
                    throw err if err?
                    minified_js = compressScriptCode(data.toString())
                    fs.writeFile file_path, minified_js, (err) ->
                        throw err if err?
                        num_compressed += 1
                        if num_compressed is asset_list.length
                            callback?()
 
 
 
 
compressScriptCode = (js_script_code) ->
    toplevel_ast = UglifyJS.parse(js_script_code)
    toplevel_ast.figure_out_scope()
 
    compressor = UglifyJS.Compressor
        drop_debugger   : true
        warnings        : false
    compressed_ast = toplevel_ast.transform(compressor)
    compressed_ast.figure_out_scope()
    compressed_ast.mangle_names()
 
    min_code = compressed_ast.print_to_string()
    return min_code
 
class File
    constructor: (path, file_stats) ->
        @path = path
        @name = path.replace(ASSET_OUTPUT, '')
        @size = file_stats.size
        @mime_type = mime.lookup(@name)
        @_contents = null
 
    getContents: (cb) ->
        unless @_contents
            fs.readFile @path, (err, data) =>
                throw err if err?
                @_contents = data
                cb?(@_contents)
        else
            cb?(@_contents)
    upload: (key_prefix, cb) ->
        console.log 'uploading', @size, 'bytes\t', @name, '\t\t', @mime_type
        target_key = "#{ key_prefix }#{ @name }"
        if not s3?
            throw new Error('S3 not configured. File#upload must be called through pushAssetsToS3.')
        @getContents (contents) =>
            s3.putObject
                Bucket      : ENV.S3_BUCKET_NAME
                Key         : target_key
                Body        : contents
                ACL         : 'public-read'
                ContentType : @mime_type
            , (err, data) ->
                throw err if err
                console.log 'uploaded:', target_key
                cb()
 
 
discoverAssets = (options, callback) ->
    asset_list = []
    walker = walk.walk(ASSET_OUTPUT)
    walker.on 'file', (root, file_stats, next) ->
        unless file_stats.name[0] is '.'
            asset_list.push(new File(path.join(root, file_stats.name), file_stats))
        next()
    walker.on 'end', ->
        hashFiles asset_list, (asset_hash) ->
            callback(asset_list, asset_hash)
 
 
 
 
pushAssetsToS3 = (options, callback) ->
 
    AWS.config.update
        accessKeyId     : ENV.AWS_ACCESS_KEY_ID
        secretAccessKey : ENV.AWS_SECRET_ACCESS_KEY
    s3 = new AWS.S3()
 
    discoverAssets options, (asset_list, asset_hash) ->
        console.log asset_hash + ':', asset_list.length, 'assets'
        uploaded_files = []
        if asset_list.length is 0
            callback?()
        else
            key_prefix = "#{ ENV.PUBLICATION_SHORT_NAME }/#{ asset_hash }/"
            asset_list.forEach (file_obj) ->
                file_obj.upload key_prefix, ->
                    uploaded_files.push(file_obj)
                    if uploaded_files.length is asset_list.length
                        new_static_url = "http://#{ ENV.S3_BUCKET_NAME }/#{ key_prefix }"
                        callback?(new_static_url)
 
 
# Actual task functions
 
doBuild = (options={}, callback) ->
    console.log 'Building...'
    doFlushStatic options, ->
        doBuildOther options, ->
            doBuildScripts options, ->
                doBuildStyles options, ->
                    callback?()
                    console.log 'Build done!'
 
 
doWatch = (options={}, callback) ->
    doFlushStatic options, ->
        doBuildOther options, ->
            doWatchScripts options, ->
                doWatchStyles options, ->
                    callback?()
 
doInitEnv = (options={}, callback) ->
    if fs.existsSync(path.join(PROJECT_ROOT, '.env')) and not options.force
        throw new Error('.env exists. Already initialized?')
 
    crypto.randomBytes 32, (err, secret_key) ->
        env_template = """
        CACHE_SOFT_EXPIRY=10
        CONTENT_API_TOKEN=
        CONTENT_API_ROOT=marquee.by/content/
        DEBUG=True
        ENVIRONMENT=development
        PUBLICATION_NAME=
        PUBLICATION_SHORT_NAME=
        STATIC_URL=/static/
        SECRET_KEY=#{ secret_key.toString('hex') }
        """
        env_development_template = """
        AWS_ACCESS_KEY_ID=
        AWS_SECRET_ACCESS_KEY=
        S3_BUCKET_NAME=cdn.mrqe.co
        """
 
        operations = 0
        next = ->
            operations += 1
            if operations is 2
                callback?()
 
        fs.writeFile ENV_FILE, env_template, (err) ->
            throw err if err?
            console.log 'Wrote .env'
            next()
 
        fs.writeFile ENV_DEVELOPMENT_FILE, env_development_template, (err) ->
            throw err if err?
            console.log 'Wrote .env-development'
            next()
 
 
doInit = (options={}, callback) ->
    doInitEnv options, ->
 
        operations = 0
        next = ->
            operations += 1
            if operations is 2
                console.log 'Initialized. Next, fill out env variables, add origin and heroku git remotes.'
 
        fs.mkdirs path.join(PROJECT_ROOT, 'static_source'), (err) ->
            throw err if err?
            console.log 'Made `static_source/`'
            next()
 
        executeCommand ['rm', '-rf', '.git'], options, ->
            executeCommand ['git', 'init'], options, ->
                console.log 're-initialized git'
                upstream_command = ['git','remote','add','upstream','git@git.droptype.com:offsite-publication-boilerplate.git']
                executeCommand upstream_command, options, ->
                    console.log 'upstream remote added'
                    next()
 
 
doFlushStatic = (options={}, callback) ->
    console.log 'Flushing static'
    fs.removeSync(ASSET_OUTPUT)
    fs.mkdirsSync(ASSET_OUTPUT)
    callback?()
 
 
doBuildScripts = (options={}, callback) ->
    console.log 'Building scripts'
    coffee_command = [
        'coffee',
        '--output', ASSET_OUTPUT
        '--compile', ASSET_SOURCE
    ]
    executeCommand coffee_command, options, ->
        if options.production
            minifyScripts options, ->
                callback?()
        else
            callback?()
 
 
doBuildStyles = (options={}, callback) ->
    console.log 'Building styles'
    compass_command = makeCompassCommand('compile', options)
    executeCommand(compass_command, options, callback)
 
 
doWatchScripts = (options={}, callback) ->
    coffee_command = [
        'coffee',
        '--watch',
        '--output',  ASSET_OUTPUT
        '--compile', ASSET_SOURCE
    ]
    spawnCommand(coffee_command, callback)
 
 
doWatchStyles = (options={}, callback) ->
    compass_command = makeCompassCommand('watch', options)
    spawnCommand(compass_command, callback)
 
doDeployStatic = (options={}, callback) ->
    setUpEnv()
    options.production ?= true
    doBuild options, ->
        pushAssetsToS3 options, (new_static_url) ->
            update_static_url_command = ['heroku','config:set', "STATIC_URL=#{ new_static_url }"]
            # console.log '\n\n\t*** Now run this:', update_static_url_command.join(' '), '\n\n'
            success = ->
                console.log 'Set heroku STATIC_URL'
                callback?()
            error = (err) ->
                console.log err
                console.log '\n** Probably not a heroku app. You can ignore that.'
                callback?()
            executeCommand(update_static_url_command, options, success, error)
 
 
doBuildOther = (options={}, callback) ->
    walker = walk.walk(ASSET_SOURCE)
    to_copy = []
    console.log 'walking', ASSET_SOURCE
    walker.on 'file', (root, file_stats, next) ->
        unless file_stats.name[0] is '.' or file_stats.name.split('.').pop() in ['sass', 'coffee']
            to_copy.push(path.join(root, file_stats.name))
        next()
    walker.on 'end', ->
        if to_copy.length is 0
            callback?()
        else
            num_copied = 0
            to_copy.forEach (f) ->
                source = f
                destination = f.replace(ASSET_SOURCE, ASSET_OUTPUT)
                copyFile = ->
                    fs.copy source, destination, (err) ->
                        throw err if err?
                        num_copied += 1
                        if num_copied is to_copy.length
                            console.log "#{ num_copied } copied"
                            callback?()
                path_parts = destination.split(path.sep)
                if path_parts.length > 1
                    path_parts.pop()
                    console.log path_parts.join(path.sep)
                    fs.mkdirs path_parts.join(path.sep), (err) ->
                        throw err if err?
                        copyFile()
                else
                    copyFile()
 
 
 
 
# Task definitions
 
task 'init'             , 'Initialize the project'                                      , doInit
task 'init:env'         , 'Initialize just the env files (-f to overwrite)'             , doInitEnv
task 'build'            , 'Compile the static sources and put it into static/'          , doBuild
task 'build:scripts'    , ''                                                            , doBuildScripts
task 'build:styles'     , ''                                                            , doBuildStyles
task 'build:other'      , ''                                                            , doBuildOther
task 'flush:static'     , 'Empty the static directory'                                  , doFlushStatic
task 'watch'            , 'Spawn coffee and compass watchers'                           , doWatch
task 'deploy:static'    , 'Deploy the static files to S3'                               , doDeployStatic
# task 'setenv'           , 'Set production environment variables from .env_production'   , doSetEnv
# task 'getenv'           , 'Get production environment variables to .env_production'     , doGetEnv