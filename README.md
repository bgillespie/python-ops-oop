# python-ops-oop

A tutorial on Python object-oriented programming for Operations folks.

To get the best from this tutorial, you need to have a _bit_ of Python programming experience, to the extent of writing scripts that perform tasks on remote devices, probably using the `requests` module.

## Getting started

You can read the tutorial right here in Github! Just navigate to the `notebooks` folder and start with `scenario_1`.

You can also clone this repository and install all the dependencies like so:

```shell
cd python-ops-oop
python3 -m venv .venv
source .venv/bin/activate
pip install --user poetry
poetry install --no-edit --with=dev
```

... then you can view the notebooks with...

```shell
jupyter notebook
```

... and head to `notebooks/scenario_1.ipynb`.

You can also have a go yourself at implementing the OOP solution by setting up the simulation like so:

```python
# Load the libraries
import os, sys, json
from tutor_router.scenarios import Scenario, NotFoundError

# Set up the scenario
scenario = Scenario.scenario_2()

# Make these look a bit like `requests` calls.
request = scenario.request
get = scenario.get
post = scenario.post

# Get a list of host names, for convenience.
hosts = tuple(scenario.hosts())
```

If you have a problem importing from `tutor_router`, its because you have to put the source directory on your `PYTHONPATH` like so:

```shell
export PYTHONPATH=<path-to-src-folder-under-python-ops-oop>
```

... before you run your script.
