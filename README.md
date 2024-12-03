# EOEPCA Demo Notebooks

Collection of Jupyter notebooks to demonstrate of Common Architecture building blocks functionalities.

## Notebooks

The notebooks are under directory [demoroot/notebooks](demoroot/notebooks), with supporting files under [demoroot/data](demoroot/data).

## Execution

To run the notebooks, you will need a Jupyter Notebook instance.

You can start one on your PC or a remote server, follow the instructions below.

### Windows

Download [WinPython (dot version)](https://winpython.github.io/) and extract it in a folder on your PC.

Download [this repository](https://github.com/EOEPCA/demo/archive/refs/heads/main.zip) and extract it in the `notebooks` sub-folder of your `WPy64` installation.

Run the `WinPython Command Prompt.exe` software in the `WPy64` folder and run the following command to install the EOEPCA demo notebook pre-requisites:

```console
python.exe -m pip install --upgrade pip
pip install -r ../notebooks/demo-main/demoroot/requirements.txt
```

Exit the `WinPython Command Prompt.exe` application and run the `Jupyter Notebook.exe` application

Open one of the notebooks in the `notebooks/demo-main/demoroot/notebooks` directory and run it.

### Linux

You can use Docker to run a local JupyterLab instance.

To do so, first install docker and docker-compose, following the [official instructions](https://docs.docker.com/engine/install/)

Then you can build the docker image with `docker-compose`:

```console
docker-compose build
```

The built container bundles the notebooks and supporting files.

To run the application you can then run

```console
docker-compose up
```

And open your browser at [http://0.0.0.0:8888](http://0.0.0.0:8888)

NOTE: To keep changes to the notebooks after the closure of the docker container, so for example for local devlopment, you can use the following command line to mount the local notebook files into the running container, via

```console
docker-compose -f docker-compose-dev.yml up
```
