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

## develop

Use the commandline arg to mount the local notebook files into the running container for local development...

```console
docker-compose -f docker-compose-dev.yml up
```
