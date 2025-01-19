# Setup
## Poetry
In base python env (cmd):
```bash
pip install poetry
```
Navigate to project folder:
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

To load/setup existing poetry environment for PyCharm project:
To get folder containing environment - in cmd in project directory:
```bash
poetry env info --path
```
Copy path to the Executable like: ```C:\Users\<user>\AppData\Local\pypoetry\Cache\virtualenvs\closest-to-you-eB-e_an6-py3.12\Scripts\python.exe```

In PyCharm:
```Settings > Python Interpreter > Add Interpreter > Add Local Interpreter > Poetry Environment > Existing >> ... (on the right of Interpreter selection bar) > paste path to the python.exe of poetry env```
