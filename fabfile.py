# CIR news applications fabfile for Heroku
# Modified from work by the Chicago Tribune's News Applications team
# We encourage you to copy this floppy (http://www.youtube.com/watch?v=up863eQKGUI)

import os
from fabric.api import *

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

"""
Base configuration
"""
env.project_name = 'rainmaker'
env.db_name = 'rainmaker'
env.s3_name = 'rainmaker'
env.database_password = '31qc3Ybvhvs'
env.site_media_prefix = "site_media"
env.admin_media_prefix = "admin_media"
env.dbserver_path = '/home/projects' % env
env.localpath = BASE_DIR
env.python = 'python2.7'

"""
Environments
"""
def production():
    """
    Work on production environment
    """
    env.settings = 'production'
    env.hosts = ['data.apps.cironline.org']
    env.user = 'projects'
    env.s3_bucket = env.s3_name

"""
Running OSX?
"""

def install_homebrew():
    """
    Installs homebrew -- the sane OSX package manager.
    """
    local('/usr/bin/ruby -e "$(curl -fsSL https://raw.github.com/gist/323731)"')

def setup_osx():
    """
    OSX is going to throw a fit if you try to bootstrap a virtualenv from the
    requirements file without doing the following. Requires homebrew. You can
    either run install_homebrew above or follow the instructions here:
    https://github.com/mxcl/homebrew/wiki/installation
    """
    local('brew install libmemcached')
    local('brew install libevent')

"""
Local bootstrap
"""

def bootstrap():
    """
    Local development bootstrap: you should only run this once.
    """
    # Install requirements
    local("pip install -r ./requirements.txt")
    
    # Create database
    create_database(local)
    local("python ./%(project_name)s/manage.py syncdb --noinput" % env)
    
    # Set virtualenv vars for local dev
    local('echo "export PROJECT_NAME=\"%(project_name)s\"" >> $WORKON_HOME/%(project_name)s/bin/postactivate' % env)
    local('echo "export DJANGO_SETTINGS_MODULE=\"%(project_name)s.settings\"" >> $WORKON_HOME/%(project_name)s/bin/postactivate' % env)
    local('echo "export PYTHONPATH=%(localpath)s:%(localpath)s/%(project_name)s" >> $WORKON_HOME/%(project_name)s/bin/postactivate' % env)
    local('echo "export PATH=$PATH:%s" >> $WORKON_HOME/%s/bin/postactivate' % (BASE_DIR, env.project_name))
    local('echo -e "*.pyc\ndata\\n%(project_name)s/gzip" > .gitignore' % env)

"""
Heroku
"""

def setup_heroku():
    """
    Performs initial setup on heroku.
    """
    local("cd %(localpath)s" % env)
    local("git init")
    local("git add .")
    local("git commit -m 'Initial commit'")
    local("heroku create -s cedar" % env)

def deploy_to_heroku():
    local("pip freeze > requirements.txt")
    local("git add .")
    prompt("Type your commit message here:", key='commitmessage')
    local("git commit -m '%(commitmessage)s';" % env)
    local("git push heroku master")

def heroku_shell():
    local("heroku run python %(project_name)s/manage.py shell --settings=%(project_name)s.settings.production")

def heroku_clear_cache():
    local("heroku run python %(project_name)s/manage.py clearcache --settings=%(project_name)s.settings.production" % env)

"""
Database setup and deploy
"""

def dump_database(func=local):
    func('pg_dump --no-owner %(db_name)s | gzip -c > %(localpath)s/data/dump.sql.gz' % env)
    
def create_database(func=run):
    """
    Creates the user and database for this project.
    """
    func('echo "CREATE USER %(db_name)s WITH PASSWORD \'%(database_password)s\';" | psql postgres' % env)
    func('createdb -O %(db_name)s %(db_name)s -T template_postgis' % env)
    func('echo "GRANT ALL PRIVILEGES ON %(db_name)s to %(db_name)s;" | psql postgres' % env)
    func('psql -c "ALTER TABLE public.spatial_ref_sys OWNER TO %(db_name)s" %(db_name)s;' % env)
    func('psql -c "ALTER TABLE public.geometry_columns OWNER TO %(db_name)s" %(db_name)s;'% env )
    
def destroy_database(func=run):
    """
    Destroys the user and database for this project.
    
    Will not cause the fab to fail if they do not exist.
    """
    with settings(warn_only=True):
        func('dropdb %(db_name)s' % env)
        func('dropuser %(db_name)s' % env)

def load_data():
    """
    Loads data from the repository into PostgreSQL.
    """
    with settings(warn_only=True):
        run("mkdir %(dbserver_path)s/data/%(db_name)s" % env)
    local("scp %(localpath)s/data/dump.sql.gz %(user)s@data.apps.cironline.org:data/%(db_name)s" % env)
    run("gunzip %(dbserver_path)s/data/%(db_name)s/dump.sql.gz" % env)
    run('psql -U %(db_name)s -q %(db_name)s < %(dbserver_path)s/data/%(db_name)s/dump.sql' % env)
    
def pgbouncer_down():
    """
    Stop pgpool so that it won't prevent the database from being rebuilt.
    """
    sudo('/etc/init.d/pgbouncer stop')
    
def pgbouncer_up():
    """
    Start pgpool.
    """
    sudo('/etc/init.d/pgbouncer start')

def deploy_data():
    dump_database()
    destroy_database()
    create_database()
    load_data()

"""
Static media
"""

def gzip_assets():
    """
    GZips every file in the assets directory and places the new file
    in the gzip directory with the same filename.
    """
    local('cd %s; python ./gzip_assets.py' % BASE_DIR)

def deploy_to_s3():
    """
    Deploy the latest project site media to S3.
    """
    env.gzip_path = '%(localpath)s/%(project_name)s/gzip/static/' % env
    local(('s3cmd -P --add-header=Content-encoding:gzip --guess-mime-type --rexclude-from=%(localpath)s/s3exclude sync %(gzip_path)s s3://%(s3_bucket)s/%(s3_name)s/%(site_media_prefix)s/') % env)

def deploy_static():
    local("python ./%(project_name)s/manage.py collectstatic" % env)
    gzip_assets()
    deploy_to_s3()

"""
Deaths, destroyers of worlds
"""
def shiva_the_destroyer():
    """
    Remove all directories, databases, etc. associated with the application.
    """
    with settings(warn_only=True):
        prompt("What's the name of your app on Heroku? (ex. strong-sword-3895):", key='appname')
        local('heroku apps:destroy --app %(appname)s' % env)
        destroy_database()
        run('s3cmd del --recursive s3://%(s3_bucket)s/%(s3_name)s' % env)

def shiva_local():
    """
    Undo any local setup.  This will *destroy* your local database, so use with caution.
    """    
    destroy_database(local)
    
"""
3 ... 2 ... 1 ... blastoff
"""

def blastoff():
    deploy_data()
    deploy_static()
    deploy_to_heroku()
