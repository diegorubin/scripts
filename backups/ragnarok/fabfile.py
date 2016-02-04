import time
from fabric.api import env, roles, run

DESTINY_PATH = "/tmp/backups"


def create_output_directory():

    run("mkdir -p %s" % DESTINY_PATH)


def copy_mongodb_databases():

    databases = env.mongodatabases.split(',')

    for database in databases:
        run("mongodump -h %s -d %s -o %s" % (env.mongohost, database, DESTINY_PATH))


def copy_mysql_databases():

    run("mysqldump -u%s -p%s --all-databases > %s/mysql.sql"%(env.mysqluser, env.mysqlpasswd, DESTINY_PATH))


def generate_tarball(timestamp):

    run("tar -jcvf /tmp/backup-%s.tar.bz2 %s" % (timestamp, DESTINY_PATH))

    return timestamp


def copy_applications_contents():

    applications = env.applications.split(',')

    for application in applications:
        exclude = "--exclude=bin --exclude=bundle --exclude=log --exclude=pids --exclude=node_modules"
        run("tar -zcvf %s/%s-application.tar.gz %s /applications/%s/shared" %
            (DESTINY_PATH, application, exclude, application))


def cryptfile(timestamp):

    # to decrypt: echo password | gpg --batch -q -o file.tar.bz2 --passphrase-fd 0 --decrypt file.tar.bz2.gpg
    run("echo %s | gpg --batch -q --passphrase-fd 0 --cipher-algo AES256 -c /tmp/backup-%s.tar.bz2" %
        (env.passphrase, timestamp))


def sync():

    run("mv /tmp/backup-*.tar.bz2.gpg %s/%s" % (env.grivepath, env.driverbackuppath))
    run("grive -p %s -s %s" % (env.grivepath, env.driverbackuppath))


def clear_backup_path():

    run("rm -rf /tmp/backup*")


def backup(commands):

    timestamp = int(time.time())

    commands = commands.split(";")

    create_output_directory()

    if "mongodb" in commands:
        copy_mongodb_databases()

    if "mysql" in commands:
        copy_mysql_databases()

    if "applications" in commands:
        copy_applications_contents()

    generate_tarball(timestamp)
    cryptfile(timestamp)
    sync()
    clear_backup_path()

