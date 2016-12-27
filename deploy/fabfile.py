from fabric.api import env, run

def start_container():
    command = ['docker run --net=host -d']
    command.append("--name %s"%(env.container))

    for variable in env.variables.split(';'):
        command.append("-e %s"%(variable))

    for volume in env.volumes.split(';'):
        command.append("-v %s"%(volume))

    for port in env.ports.split(';'):
        command.append("-p %s"%(port))

    command.append("%s:%s"%(env.image, env.version))

    run(' '.join(command))

def remove_container():
    run("docker rm %s || echo 'not exists'"%(env.container))

def stop_container():
    run("docker stop %s || echo 'not running'"%(env.container))

def update_docker_image():
    run("docker pull %s:%s"%(env.image, env.version))

def deploy():
    stop_container()
    remove_container()
    update_docker_image()
    start_container()

