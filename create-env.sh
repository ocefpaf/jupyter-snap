# Creating the conda-environment for the jupyter snap.

# Local install.
LOCAL_INSTALL="JUPYTER"

# 393 MB JUPYTER
conda create --yes \
             --prefix ${LOCAL_INSTALL}  \
             python=3.7 \
             notebook \
             jupyter_console \
             nbconvert \
             ipykernel \
             ipywidgets

# 263 MB JUPYTER
conda remove --yes pandoc --force-remove --prefix ${LOCAL_INSTALL}

# 232M JUPYTER
find ${LOCAL_INSTALL} -type d -name '__pycache__' -exec rm -rf "{}" \;

# This step is not to reduce the size but to avoid the snap "thinking" it is a conda-env.
rm -rf ${LOCAL_INSTALL}/conda-meta
