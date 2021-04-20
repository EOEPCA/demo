FROM jupyter/scipy-notebook:latest

USER ${NB_USER}

WORKDIR ${HOME}/work

COPY --chown=${NB_UID}:${NB_GID} /ipyauth /ipyauth
RUN cd /ipyauth && conda create -n dev-ipyauth python=3 && source activate dev-ipyauth && pip install notebook && pip install -r requirements.txt
RUN conda install jupyterlab nodejs -c conda-forge
RUN cd /ipyauth/ipyauth/js && npm install

COPY --chown=${NB_UID}:${NB_GID} demoroot .

RUN pip install -U -r requirements.txt
RUN jupyter serverextension enable --py --sys-prefix ipyauth.ipyauth_callback
RUN jupyter nbextension install --py --symlink --sys-prefix ipyauth.ipyauth_widget
RUN jupyter nbextension enable ipyauth.ipyauth_widget --py --sys-prefix
RUN jupyter labextension link /ipyauth/ipyauth/js --no-build
RUN jupyter labextension install @jupyter-widgets/jupyterlab-manager --no-build
RUN jupyter lab build
CMD [ "jupyter", "lab", "--NotebookApp.token=''" ]
