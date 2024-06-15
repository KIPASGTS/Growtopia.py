[![Github Action](https://img.shields.io/github/actions/workflow/status/KIPASGTS/GrowtopiaPrivateServer-Python/main.yml?branch=main&logo=github&logoColor=white)](https://github.com/KIPASGTS/GrowtopiaPrivateServer-Python/branches)
<h1 align="center">Growtopia Private Server Python</h1>

An Growtopia private server made with python3 using enet wrapper with [PyEnet](https://github.com/aresch/pyenet)

## Todo
- [X] World Handler
- [ ] Multiplayer (not tested)
- [X] World Saving
- [X] Player Saving
- [ ] Player Inventory
- [X] Player Movement
- [ ] Improvement Security
- [ ] Tile Extra Handler
- [ ] Player Command
- [ ] Player Chat Input
- [X] Player leave world
- [X] Player enter world
- [X] Show world offer

## Requiredment
- Python 3.13 or higher
- GCC (GNU Compiler Collection)
- Cython
  
## Installation
To install the server, run the following commands:
```
$ python -m pip install setuptools
$ python -m pip install Cython
$ python setup.py build
$ python setup.py install
```

## Run Server
Start the server with the command:
```
$ python server.py
```

## Credits:
- [ENet](https://github.com/lsalzman/enet): ENet reliable UDP networking library
- [PyEnet](https://github.com/aresch/pyenet): An ENet Python3 Wrapper