FROM jupyter/scipy-notebook:latest

USER ${NB_USER}

WORKDIR ${HOME}/work

COPY --chown=${NB_UID}:${NB_GID} demoroot .

RUN pip install -U -r requirements.txt

CMD [ "jupyter", "lab", "--NotebookApp.token=''" ]
