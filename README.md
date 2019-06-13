# Creating a Jupyter snap based on a conda-environment

[![Get it from the Snap Store](https://snapcraft.io/static/images/badges/en/snap-store-black.svg)](https://snapcraft.io/jupyter)

Q: What is a snap?

A: Snaps are containerised software packages that are simple to create and install. They auto-update and are safe to run. And because they bundle their dependencies, they work on all major Linux systems without modification.

Q: Why use conda environments to create a snap?
A: conda environments are a "solved" set of relocatable packages that fill almost all of the prerequisites for a snap. It is quite easy to go from a environment to an "spp."

The snap was based on a conda environment with jupyter.

## Steps to create the snap

The conda environment was created with,

$ conda create --name JUPYTER python=3.7 notebook jupyter_console nbconvert ipykernel ipywidgets

in order to avoid `qt` and reduce the snap size we did not use the `jupyter` metapackage and did not install `qtconsole`.

Before "snapping" we remove all the `__pycache__` directories and removed `pandoc`,
an optional `nbconvert` dependency. After that the compressed snap went from 233 MB to 68 MB.  See `create-env.sh` for more details.

Once the environment is created and cleaned we can install `snapcraft` to create,
test, and upload the snap.

1. Install snacraft with the "classic" option.

```shell
$ snap install snapcraft --classic
```

2. Start a new project.

```shell
$ snacraft init
```

then edit the snap/snacraft.yaml file. One can also add plugins to modify the snap creation and add Desktop files. Check the snap folder to see the jupyter snap final form.

3. Build the project

```shell
$ snapcraft --destructive-mode
```

`--destructive-mode` means "use host" and not any sort of clean-up!

4. Test it

```shell
$ snap try --devmode
```

5. Remove it in case you need to rebuild it

```shell
$ snapcraft clean --destructive-mode
```

6. Push it to the store

```shell
$ snacraft push --release=stable jupyter_1.0.0_amd64.snap
```

These steps should be automated in a CI and every-time a new release of one of the packages is create it should trigger a snap rebuild.

and check https://snapcraft.io/jupyter/publicise
