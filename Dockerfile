FROM jupyter/scipy-notebook:lab-3.0.14

# Use the built-in user
USER ${NB_USER}

# Install the python requirements in an early layer,
# since it shouldn't change that often and takes a while to execute.
WORKDIR ${HOME}/work/demoroot
COPY --chown=${NB_UID}:${NB_GID} demoroot/requirements.txt .
RUN pip install -U -r requirements.txt

# Copy across the demo files
WORKDIR ${HOME}/work
COPY --chown=${NB_UID}:${NB_GID} demoroot .
