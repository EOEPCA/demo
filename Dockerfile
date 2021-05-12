FROM jupyter/scipy-notebook:lab-3.0.14

USER ${NB_USER}

WORKDIR ${HOME}/work

COPY --chown=${NB_UID}:${NB_GID} demoroot .

RUN pip install -U -r requirements.txt

