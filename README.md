# demo

Demonstration of Common Architecture building blocks.

Uses docker-compose to run the demo in a local JupyterLab instance.

## notebooks

The notebooks are under directory 'demoroot/notebooks', with supporting files under 'demoroot/data'.

## build

The docker image is built with `docker-compose`:

```console
docker-compose build
```

The built container bundles the notebooks and supporting files.

## run

```console
docker-compose up
```

Open your browser at [http://0.0.0.0:8888](http://0.0.0.0:8888)

## develop

Use the commandline arg to mount the local notebook files into the running container for local development...

```console
docker-compose -f docker-compose-dev.yml up
```

## How to develop on Apple M1 and M2 ARM chips

**Step 1**

Install and run the tonistiigi/binfmt emulator for different architectures with this Docker image:

```sh
docker run --privileged --rm tonistiigi/binfmt --install all
```

More information about this image can be found at [tonistiigi Docker hub](https://hub.docker.com/r/tonistiigi/binfmt).

**Step 2**

Adjust the docker-compose-dev.yml volume paths to match your system

For example:

```yml
    volumes:
    - ${PWD}/demoroot:/home/${PUSER}/work
    - ${PWD}/kubeconfig:/home/${PUSER}/.kube/config
    - ${DEPLOYMENT_GUIDE_ROOT}/Users/${PUSER}/EOEPCA/deployment-guide
```

**Step 3**

Run the following command to start the Jupyterlab:

```sh
PUSER=username PUID=userID PGID=groupID docker-compose -f docker-compose-dev.yml up
```

To obtain the correct values open the terminal and user the following commands:

**PUSER:**

```sh
whoami
```

**PUID:**

```sh
id -u
```

**PGID:**

```sh
id -g
```
