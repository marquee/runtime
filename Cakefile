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



# Actual task functions

doBuild = (options={}, callback) ->
    console.log 'Building...'
    doFlushStatic options, ->
        doBuildScripts options, ->
            doBuildStyles options, ->
                callback?()
                console.log 'All done!'


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
    compass_extra_options = [
        '--relative-assets',
        '--require',            'compass-normalize',
        '--sass-dir',           ASSET_SOURCE,
        '--css-dir',            ASSET_BUILD,
        '--images-dir',         ASSET_SOURCE,
        '--javascripts-dir',    ASSET_BUILD,
    ]

    compass_command = ['compass', 'compile', '--force']
    compass_command.push('--environment')
    if options.production
        compass_command.push('production')
    else
        compass_command.push('development')

    compass_command.push(compass_extra_options...)

    executeCommand(compass_command, options, callback)



# Task definitions

task 'build'            , 'Compile the static sources and put it into static/'          , doBuild
task 'build:scripts'    , ''                                                            , doBuildScripts
task 'flush_static'     , 'Empty the static directory'                                  , doFlushStatic
# task 'deploy:static'    , 'Deploy the static files to S3'                               , doDeployStatic
# task 'setenv'           , 'Set production environment variables from .env_production'   , doSetEnv
# task 'getenv'           , 'Get production environment variables to .env_production'     , doGetEnv



