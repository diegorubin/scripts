import time
from fabric.api import env, run, sudo

DESTINY_PATH = "/tmp/backups"


def create_output_directory():

    run("mkdir -p %s" % DESTINY_PATH)


def copy_mongodb_databases():

    databases = env.mongodatabases.split(',')

    for database in databases:
        run("mongodump -h %s -d %s -o %s" % (env.mongohost, database, DESTINY_PATH))


def copy_mysql_databases():
    command = ["mysqldump -u%s" % env.mysqluser]
    if env.mysqlpasswd:
        command.append("-p%s" % env.mysqlpasswd)
    command.append("--all-databases")

    run("%s > %s/mysql.sql" % (' '.join(command), DESTINY_PATH))


def generate_tarball(timestamp):

    run("tar -jcvf %s %s" % (__get_tarball_filename(timestamp), DESTINY_PATH))

    return timestamp


def copy_applications_contents():

    applications = env.applications.split(',')

    for application in applications:
        exclude = "--exclude=bin --exclude=bundle --exclude=log --exclude=pids --exclude=node_modules"
        run("tar -zcvf %s/%s-application.tar.gz %s /applications/%s/shared" %
            (DESTINY_PATH, application, exclude, application))


def copy_custom_directories_contents():

    directories = env.custom_directories.split(',')

    for directory in directories:

        path = getattr(env, "custom_directory_%s_path" % directory)
        options = getattr(env, "custom_directory_%s_options" % directory)

        is_sudo = ""
        if hasattr(env, "custom_directory_%s_sudo" % directory):
            is_sudo = getattr(env, "custom_directory_%s_sudo" % directory)

        destiny_file = "%s/%s-directory.tar.gz" % (DESTINY_PATH, directory)

        command = "tar -zcvf %s %s %s" % (destiny_file, options, path)

        if is_sudo in ["true", "True", "1", "yes", "y", "t"]:
            sudo(command)
            sudo("chown  %s %s" % (env.user, destiny_file))
        else:
            run(command)


def cryptfile(timestamp):

    # to decrypt: echo password | gpg --batch -q -o file.tar.bz2 --passphrase-fd 0 --decrypt file.tar.bz2.gpg
    run("echo %s | gpg --batch -q --passphrase-fd 0 --cipher-algo AES256 -c %s" %
        (env.passphrase, __get_tarball_filename(timestamp)))


def sync(timestamp):

    run("mv %s.gpg %s/%s" % (__get_tarball_filename(timestamp), env.grivepath, env.driverbackuppath))
    run("grive -p %s -s %s" % (env.grivepath, env.driverbackuppath))


def clear_backup_path(timestamp):

    run("rm -rf %s" % DESTINY_PATH)
    run("rm  %s" % __get_tarball_filename(timestamp))


def copy_systemv_service():

    destiny_service_path = "%s/systemv_services" % (DESTINY_PATH)
    run("mkdir -p %s" % destiny_service_path)

    services = env.services.split(',')
    for service in services:
        run("cp /etc/init.d/%s %s" % (service, destiny_service_path))


def backup():

    timestamp = int(time.time())

    commands = env.commands.split(',')

    create_output_directory()

    if "mongodb" in commands:
        copy_mongodb_databases()

    if "mysql" in commands:
        copy_mysql_databases()

    if "applications" in commands:
        copy_applications_contents()

    if "systemv" in commands:
        copy_systemv_service()

    if "custom_directories" in commands:
        copy_custom_directories_contents()

    generate_tarball(timestamp)
    cryptfile(timestamp)
    sync(timestamp)
    clear_backup_path(timestamp)


def __get_tarball_filename(timestamp):

    return "/tmp/%s-%s.tar.bz2" % (env.host, timestamp)

