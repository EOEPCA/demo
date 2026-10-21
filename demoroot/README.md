# eoepca-demoroot

Notebook 04 creates a private collection and checks access with two users.
Notebook 05 uploads files to a workspace and shows how to share them.

From the repository root:

```sh
cd demoroot
uv sync --locked
uv run jupyter lab --notebook-dir=notebooks
```

Open a notebook in `notebooks/`. Both use `notebooks/eoepca-demo.env` for settings.
