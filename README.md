## Install

The project uses Poetry, a package and virtual environment manager for Python.  
Installation instructions for poetry are [here](https://python-poetry.org/docs/). 
A TLDR is to do 

```
curl -sSL https://install.python-poetry.org | python3 - --version 1.4.2
```

and then add `$HOME/.local/bin` to the Path. 
```
export PATH="$HOME/.poetry/bin:$PATH"
```

Check for installation using `poetry --version` and make sure it shows `1.4.2`.

Once you have Poetry setup, you can simply go to the root of the directory and do

```
make install
```

## Tests

The project has static checks, which checks for formatting and typing.

Invoke static checks using

```
make check
```

The project uses `pytest` for unit testing. Run all tests using

```
make test
```


## Run

Once the package is installed, it is available as a CLI utility `wgs_filetree_metadata`.
All options for the utility can be obtained by invoking `wgs_filetree_metadata --help`.
There is a sample file available, sourced from 
[GitHub](https://raw.githubusercontent.com/indivumed/application-exercises/master/filetree-sample-data.json)
at the path `data/filetree-sample-data.json`.

An example way to run it would be the following 

```
wgs_filetree_metadata --input-file data/filetree-sample-data.json --output-file data/filetree_metadata.json 
```


## Run using Docker

The package also includes the capability to use Docker to run the tool for easy reproducibility.
The command has to be present as an environment variable CMD.
To run, make sure Docker is running and then do the following.

```
CMD="wgs_filetree_metadata --input-file data/filetree-sample-data.json data/filetree_metadata.json" docker-compose up
```