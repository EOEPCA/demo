# demo

Demonstration of Common Architecture building blocks.

Uses docker version of Jupyter to run the demo in a local JupyterLab instance.

## notebooks

The notebooks are under directory 'demoroot/notebooks', with supprting files under 'demoroot/data'.

## build

The docker image is built with the script `build.sh`.

The built container bundles the notebooks and supporting files.

## run

The script `run.sh` instantiates the local Jupyter Lab instance.

## develop

Use 'dev' commandline arg to mount the local notebook files into the running container for local development...
```
./run.sh dev
```
