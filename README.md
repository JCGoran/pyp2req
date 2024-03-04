# pyp2req - pyproject.toml to requirements.txt converter

Have you ever wanted to obtain the dependencies from a `pyproject.toml` file in a `requirements.txt` format (i.e. in a format you can pass to `pip install -r`)?

If so, you've found the correct tool.

## What this does

It outputs all of the various dependencies defined in [PEP 621](https://peps.python.org/pep-0621/) and [PEP 518](https://peps.python.org/pep-0518/) (to be more specific, it supports `project.dependencies`, `project.optional-dependencies`, and also `build-system.requires`) in a `requirements.txt`-compatible format to the standard output.

## What this does not do

- validate a given `pyproject.toml` file (or that the dependencies can be resolved for that matter)
- parse any requirements from any tool-specific key (like `[tool.poetry.dependencies]`)
- read any of the other keys from the `pyproject.toml` file
- parse any "dynamic" dependency specifications (as supported by [some tools](https://setuptools.pypa.io/en/latest/userguide/pyproject_config.html#dynamic-metadata))

## Why is this useful?

In case you have a project which already has a build system (say, CMake), and wish to extend it to use `pyproject.toml` (for instance, if you want to distribute wheels), but do not want the hassle of going through the `pyproject.toml` file just to extract the dependencies.

## Why not use X instead?

- pip: does not support actually parsing the `pyproject.toml` file, or installing only the dependencies without also installing the main project (keep a close eye on [this issue](https://github.com/pypa/pip/issues/11440) and [PEP 735](https://peps.python.org/pep-0735/) though!)
- Poetry: can install optional dependencies, but only those defined in the `[tool.poetry]` key
- pip-tools: close, but it actually does too much, and pins _all_ dependencies (including any transitive dependencies) to specific versions, which is great if you want to be very strict with your versioning, but not so much if want to be a bit more relaxed. It also tries to resolve all of the dependencies first, making it a bit slow

## Okay, how do I use this then?

To install from PyPI:

```sh
pip install pyp2req
```

To get all dependencies, pass the directory containing the `pyproject.toml` file as the argument:

```sh
pyp2req /path/to/dir_with_pyproject
```

For instance, here's the output of `pyp2req` on this project:

```sh
# build time dependencies
setuptools
setuptools-scm>=8.0.0
# run time dependencies
tomli;python_version<'3.11'
```

## Customization

By default, all of the dependencies (build, run, optional) are shown, but this can be customized.

### Removing build system dependencies

Run:

```sh
pyp2req -b /path/to/dir_with_pyproject
```

### Removing run dependencies

Run:

```sh
pyp2req -r /path/to/dir_with_pyproject
```

### Only selecting certain optional dependencies

Run:

```sh
pyp2req -t [TYPE] /path/to/dir_with_pyproject
```

where you can replace `[TYPE]` with any of the optional dependencies specified (it's also additive, meaning you can specify multiple dependencies).

Note that if you _only_ want the optional dependencies, you need to disable the build and run dependencies by adding `-b -r` to the above invocation.

### Listing optional dependencies

PEP 621 specifies that `optional-dependencies` should not be a list, but rather a dictionary, meaning you can specify groups of dependencies (for instance, `test`, `docs`, etc.), so you may wish to figure what those are first.
In order to make life easier, you can run:

```sh
pyp2req -l /path/to/dir_with_pyproject
```

which will list all of the optional groups that are defined in the project.
Note that using this option makes the program ignore any other option specified.

### Removing comments

You can output a version without comments using:

```sh
pyp2reqs -c /path/to/dir_with_pyproject
```

## License

MIT

## FAQ

### I keep getting the message `error: the following arguments are required: dir` when I use the `-t` option

There are 2 solutions here:

1. put the arguments to the `-t` option _after_ specifying the directory: `pyp2req /path/to/dir_with_pyproject -t typ1 typ2`
2. use `--` to signify end of parsing options and start of mandatory arguments: `pyp2req -t typ1 typ2 -- /path/to/dir_with_pyproject`

### Can I directly install the requirements using `pip` without saving to a file?

In Bash and Zsh shells (Linux and MacOS defaults) you can take advantage of [process substitution](https://en.wikipedia.org/wiki/Process_substitution):

```sh
pip install -r <(pyp2req /path/to/dir_with_pyproject)
```
