FROM jupyter/scipy-notebook:latest

USER ${NB_USER}

COPY --chown=${NB_UID}:${NB_GID} . ${HOME}

RUN pip install -U -r requirements.txt

# ENTRYPOINT [ "tini", "-g", "--" ]
ENTRYPOINT [ "jupyter", "lab", "--NotebookApp.token=''" ]
