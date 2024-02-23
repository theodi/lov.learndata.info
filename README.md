# DIY schema.org

Welcome to DIY schema.org, a lightweight software tool for defining your own classes and properties based on the schema.org vocabulary. This software allows you to create custom schemas while reusing properties and classes already available via schema.org.

## Overview

DIY schema.org is a simplified version of the software used to build schema.org. It has been streamlined for ease of use and focuses on enabling users to define their own schemas quickly and efficiently. All tests have been removed along with most of the functionality for attic, proposed, and extension namespaces. It is intended for simple schema creation tasks.

## Quickstart

To use DIY schema.org, follow these steps:

1. **Download**: Download the software package.

2. **Do a build**:
   - Run `./software/util/buildsite.py -a` to build the site.

3. **Run the Server**:
   - Execute `./software/devserv.py` to run the server.

4. **Change the URI base**:
   - Open `software/SchemaTerms/sdotermsource.py` and set `DEFVOCABURI` to your base URI (e.g., `https://example.com`).
   - Open `docs/pretty-markup/layout.js` and set `VOCAB_URI` to your base URI (e.g., `var VOCAB_URI = 'https://example.com';`).

5. **Define your own schema and examples**:
   - Edit the files in the `data` directory to specify your schema and examples.

6. **GOTO (2)**

## Detailed installation

Before installing DIY schema.org, ensure that you have Python 3.10 or above installed on your system.

### Python Virtual Environment (Optional)
It is recommended to create a Python virtual environment to avoid conflicts with other Python activities on your system. For instructions on how to create virtual environments, refer to the [Python documentation](https://docs.python.org/3.7/library/venv.html).

### Install Dependencies
DIY schema.org depends on a small number of Python libraries. To install these dependencies, run the following command in the root directory of the schemaorg repository:

```bash
pip install -r software/requirements.txt
```

All commands and scripts should be executed from the root schemaorg directory.

#### Module Not Found Errors
If you encounter a "ModuleNotFoundError: No module named 'module_name'" error when running local scripts, it may be due to:
- Your Python environment not being correctly set to 3.10 or above.
- Missing required modules due to new dependencies or changes.

To ensure you have the correct modules installed, re-run the command:

```bash
pip install -r software/requirements.txt
```

### Initial Build
After cloning the repository and setting up the Python environment, run the following command for the initial build:

```bash
./software/util/buildsite.py -a
```

This command creates a local working copy of the schema.org website in the site directory.

### buildsite.py
The `buildsite.py` script is responsible for creating and managing a local image website as a set of static HTML pages and downloadable files in the site directory. It constructs this from local working copies of the files in the repository. The contents of the site directory are not committed and stored in the repository. The site directory image serves two main purposes:
1. It provides a local work-in-progress representation of the website for local testing and debugging.
2. It provides an image of the website that can be deployed.

After running the initial build, you can further customize your schema and examples before deploying or testing locally.

## Feedback

We welcome feedback and contributions to DIY schema.org. If you encounter any issues or have suggestions for improvements, please feel free to [open an issue](https://github.com/theodi/diyschema/issues) or submit a pull request.

Happy schema designing!