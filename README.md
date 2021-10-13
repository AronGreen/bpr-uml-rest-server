# bpr-uml-rest-server



## Onboarding notes

In this section notes about tools and packages should be added. Please add an appropriate heading along with a description of the subject.

### Python Virtual Environments (venv)

In order to make sure the project has the exact Python and package versions needed, we use venv. This creates a virtual environment for the project with its own installation of Python an packages - totally separate from other projects you may use.

**Setting up the environment:**

In the root project folder, run: `py -m venv .venv`

This should only be done once after cloning the project.

**Activating the environment:**

From powershell run: `.\.venv\Scripts\Activate.ps1` from the project root folder.

Your terminal should now be prefixed with `(.venv)`

With the environment active, all pip commands run locally to the project.

**Installed packages and source control:**

If you install a package in the project, you must check in the change in git, we do that by generating a `requirements.txt` file and checking that in. Here is how in powershell:

`pip freeze | Out-File -FilePath .\requirements.txt`

on the other end, restoring packages is done with pip:

`pip install -r requirements.txt`

**Further reading:**

[Python docs: Virtual Environments and Packages](https://docs.python.org/3/tutorial/venv.html)

[Pythin docs: pip](https://docs.python.org/3/installing/index.html#installing-index)



### Environment variables (dotenv)

This project uses python-dotenv to manage secrets and configuration.

The benefit is that we can setup live environment variables on our hosting provider and read local environment variables from a file - all using the same code. 

**.env**

In the root of the project, you must keep a file named `.env`, this will contain secrets and configuration.

In the root of the project you will find `.env.example` which you can copy and rename to `.env`. The file contains dummy values which you should replace. Ask a collaborator for help if needed. 

*IMPORTANT:*  It is important to never check this file into git as this will expose secrets and possibly break builds.

**settings.py**

In order to streamline the code all access of environment variables is done via the `settings.py` module.

**Adding a new variable** 

When adding a new variable, just add it in `.env` and `settings.py` (follow the patterns already established). Also add it to `.env.example` with a dummy value.

[python-dotenv docs](https://pypi.org/project/python-dotenv/)