# Setup
## Poetry installation
In base python env (cmd):
```bash
pip install poetry
```

## Poetry - if ```pyproject.toml``` exists
In cmd, in project root directory:
```bash
poetry install
```
Then jump to ```Load existing...``` below

## Poetry - if ```pyproject.toml``` is not present
In cmd, navigate to project folder:
```bash
cd <project_path>
```
Initialize ```pyproject.toml```
```bash
poetry init
```
Actually create the environment by installing any package:
```bash
poetry add django
```

Then jump to ```Load existing...``` below

# Load existing poetry environment for PyCharm project:

To get folder containing environment - in cmd in project directory:
```bash
poetry env info --path
```
Copy path to the Executable like: ```C:\Users\<user>\AppData\Local\pypoetry\Cache\virtualenvs\closest-to-you-eB-e_an6-py3.12\Scripts\python.exe```

In PyCharm:
```Settings > Python Interpreter > Add Interpreter > Add Local Interpreter > Poetry Environment > Existing >> ... (on the right of Interpreter selection bar) > paste path to the python.exe of poetry env```
