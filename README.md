# Solution

Container is just a process.

1. Chroot: isolate filesystem by changing the root directory for the specific process -> limit the access to host's other files.

2. Namespace: isolate the view of processes. Use clone or unshare to give a separate namespace for the process. By doing this, container doesn't have an access or view of other processes in the host machine.
    - Clone: [Clone](https://man7.org/linux/man-pages/man2/clone.2.html). Similar to Fork, but more finegrained flags, such as unsharing.
    - Unshare: [Unshare](https://man7.org/linux/man-pages/man2/unshare.2.html). Doesn't create a child process by default. It just disables sharing the namespace with the parent.

3. Pulling an image and running a program:
    1. Pull image from the docker registry
    2. Untar them
    3. Move all those files and any other dependencies to temporary working directory for the container(process)
    4. Change the root directory to this working directory
    5. Now, this container has all files/dependencies to run the desired program!

[![progress-banner](https://backend.codecrafters.io/progress/docker/8473d7f8-74df-44a5-8474-0c909577bc3d)](https://app.codecrafters.io/users/codecrafters-bot?r=2qF)

This is a starting point for Python solutions to the
["Build Your Own Docker" Challenge](https://codecrafters.io/challenges/docker).

In this challenge, you'll build a program that can pull an image from
[Docker Hub](https://hub.docker.com/) and execute commands in it. Along the way,
we'll learn about [chroot](https://en.wikipedia.org/wiki/Chroot),
[kernel namespaces](https://en.wikipedia.org/wiki/Linux_namespaces), the
[docker registry API](https://docs.docker.com/registry/spec/api/) and much more.

**Note**: If you're viewing this repo on GitHub, head over to
[codecrafters.io](https://codecrafters.io) to try the challenge.

# Passing the first stage

The entry point for your Docker implementation is `app/main.py`. Study and
uncomment the relevant code, and push your changes to pass the first stage:

```sh
git add .
git commit -m "pass 1st stage" # any msg
git push origin master
```

That's all!

# Stage 2 & beyond

Note: This section is for stages 2 and beyond.

You'll use linux-specific syscalls in this challenge. so we'll run your code
_inside_ a Docker container.

Please ensure you have [Docker installed](https://docs.docker.com/get-docker/)
locally.

Next, add a [shell alias](https://shapeshed.com/unix-alias/):

```sh
alias mydocker='docker build -t mydocker . && docker run --cap-add="SYS_ADMIN" mydocker'
```

(The `--cap-add="SYS_ADMIN"` flag is required to create
[PID Namespaces](https://man7.org/linux/man-pages/man7/pid_namespaces.7.html))

You can now execute your program like this:

```sh
mydocker run alpine:latest /usr/local/bin/docker-explorer echo hey
```
