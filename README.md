# NRAI Controller

Newcastle Racing AI module for control.

To start working on this project, clone this repository.

```bash
git clone --recurse-submodules https://github.com/NewcastleRacingAI/nrai_pathplanning.git
cd nrai_pathplanning
```

## Project structure

```bash
nrai_controller
├── src
│   └── nrai_controller
│       ├── node.py     # Node
│       ├── ...         # Main code
│       └── __init__.py
├── test                # Tests
└── pyproject.toml      # Python package configuration
```

## Use

### Requirements

- [Python>=3.12](https://www.python.org/downloads/release/python-3120/)
- [uv](https://docs.astral.sh/uv/)
  - Can be installed with pip globally
- Any Linux system, or WSL when ran on Windows
  - If using WSL, make sure any other modules ran simultaneously are executed in the same subsystem, or they will be unable to communicate.

### Setup

Recommended, although not mandatory: create a virtual environment.

```bash
python3 -m venv .venv
# Linux
source .venv/bin/activate
# Windows
.venv/Script/activate
```

We use [uv](https://docs.astral.sh/uv/) to automatically manage the dependencies.
Therefore, you need to install uv, either globally or in the virtual environment:

```bash
pip install uv
```

### Use

Run the script with the following command:

```bash
uv run nrai_controller
```

### Managing dependencies

If you want to add new python dependencies, use `uv add <package>` to add them automatically.

```bash
uv add numpy
```

On the other hand, if you want to remove a dependency, use `uv remove <package>`.

```bash
uv remove numpy
```

## Operation and Structure

The NRAI controller operates between two libraries, the ros_node.py file, which is serves as the main process, and the purepursuit.py file, which the ros_node.py file which hosts the pure pursuit algorithm.

The NRAI Controller receives path information (list of tuples (X, Z)) via the named pipe at `/tmp/PATHPLANNING_Path`, and propagates instructions forwards via the named pipe at `/tmp/lower_ctrl_cmd` in the schema defined [here](https://github.com/NewcastleRacingAI/nrai-NIMS/blob/main/modules/lower-controller/controller_com_spec).

## Pure pursuit

Pure pursuit is a simple control algorithm which uses the bicycle model of locomotion, which reduces a four wheeled vehicle to a two wheeled bicycle abstraction. Below is our derivation of the key parameter α in the pure pursuit algorithm found [here](https://thomasfermi.github.io/Algorithms-for-Automated-Driving/Control/PurePursuit.html), which altogether forms the basis for the implementation of pure pursuit as seen in purepursuit.py:

![](./pp.png)
