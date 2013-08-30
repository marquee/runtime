{ spawn, exec }     = require 'child_process'
util                = require 'util'
fs                  = require 'fs-extra'

# Configuration
ASSET_SOURCE   = 'static_source/'
ASSET_BUILD    = 'static/'



# Set by the -q option, determines the level of verbosity
quiet       = false
production  = false



# Options
option '-q', '--quiet',         'Suppress non-error output'
option '-p', '--production',    'Compile for production'


# Helpers

executeCommand = (command, options, callback) ->
    exec command.join(' '), (err, stdout, stderr) ->
        throw err if err
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



# Actual task functions

doBuild = (options={}, callback) ->
    console.log 'Building...'
    doFlushStatic options, ->
        doBuildScripts options, ->
            doBuildStyles options, ->
                callback?()
                console.log 'All done!'


doWatch = (options={}, callback) ->
    doFlushStatic options, ->
        doWatchScripts options, ->
            doWatchStyles options, ->
                callback?()






doFlushStatic = (options={}, callback) ->
    fs.removeSync(ASSET_BUILD)
    fs.mkdirsSync(ASSET_BUILD)
    callback?()


doBuildScripts = (options={}, callback) ->
   coffee_command = [
        'coffee',
        '--output', ASSET_BUILD
        '--compile', ASSET_SOURCE
    ]
    executeCommand(coffee_command, options, callback)


doBuildStyles = (options={}, callback) ->
    compass_command = ['compass', 'compile', '--force']
    compass_command.push('--environment')
    if options.production
        compass_command.push('production')
    else
        compass_command.push('development')

    compass_extra_options = [
        '--relative-assets',
        '--require',            'compass-normalize',
        '--sass-dir',           ASSET_SOURCE,
        '--css-dir',            ASSET_BUILD,
        '--images-dir',         ASSET_SOURCE,
        '--javascripts-dir',    ASSET_BUILD,
    ]
    compass_command.push(compass_extra_options...)

    executeCommand(compass_command, options, callback)


doWatchScripts = (options={}, callback) ->
    coffee_command = [
        'coffee',
        '--watch',
        '--output', ASSET_BUILD
        '--compile', ASSET_SOURCE
    ]
    spawnCommand(coffee_command, callback)


doWatchStyles = (options={}, callback) ->
    compass_command = ['compass', 'watch', '--force']
    compass_command.push('--environment')
    if options.production
        compass_command.push('production')
    else
        compass_command.push('development')

    compass_extra_options = [
        '--relative-assets',
        '--require',            'compass-normalize',
        '--sass-dir',           ASSET_SOURCE,
        '--css-dir',            ASSET_BUILD,
        '--images-dir',         ASSET_SOURCE,
        '--javascripts-dir',    ASSET_BUILD,
    ]
    compass_command.push(compass_extra_options...)

    spawnCommand(compass_command, callback)




# Task definitions

task 'build'            , 'Compile the static sources and put it into static/'          , doBuild
task 'build:scripts'    , ''                                                            , doBuildScripts
task 'flush_static'     , 'Empty the static directory'                                  , doFlushStatic
task 'watch'            , 'Spawn coffee and compass watchers'                           , doWatch
# task 'deploy:static'    , 'Deploy the static files to S3'                               , doDeployStatic
# task 'setenv'           , 'Set production environment variables from .env_production'   , doSetEnv
# task 'getenv'           , 'Get production environment variables to .env_production'     , doGetEnv



