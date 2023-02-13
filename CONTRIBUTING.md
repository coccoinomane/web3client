Pull requests are welcome ❤️ To start working on `web3client`, please follow these steps.

# 1. Clone the repo

This is simple:

```bash
git clone https://github.com/coccoinomane/web3client.git
```

# 2. Install dependencies

`web3client` uses [PDM](https://github.com/pdm-project/pdm/) to manage dependencies. You can install it via script:

```bash
curl -sSL https://raw.githubusercontent.com/pdm-project/pdm/main/install-pdm.py | python3 -
```

Or, if you are on Windows, you may be better off using [pipx](https://pypa.github.io/pipx/):

```bash
pipx install pdm
```

Then, to install `web3client` and its dependencies, just run:

```bash
pdm install
```

All packages, including `web3client` will be installed in a newly created virtual environment in the `.venv` folder.

# 3. Code!

`web3client` consists of two main parts:

- The client itself , in the [`src/web3client/`](./src/web3client/) folder.
- The factory, in the [`src/web3factory/`](src/web3factory/) folder.

# 4. Run tests

When you are done with your changes, please make sure to run `pdm test` before
committing to make sure that your code does not break anything.

Some tests require a local blockchain, so make sure to install
[ganache](https://www.npmjs.com/package/ganache) the first time you run `pdm
test`!

To create a new test, feel free to copy and customize an existing one: all tests
are in the [`tests`](./tests) folder.


