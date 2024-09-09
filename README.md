# Fields Extractor
This is the first part of AI autofill project. In this project I aim to extract the relevant information from html forms.

## Development

### Very initial setup

Before doing anything, do these:
1- git clone (obviously)
2- This project uses Pipenv, so install it globally!

```bash
pip3 install --user pipenv
```

3- Copy ``.env.example`` to the project root and rename it to ``.env``

5- cd the project root folder

4- Run Pipenv to install all of the dependencies:

```bash
pipenv sync
```

By default the .venv folder is located in the root folder as per ``.env`` default setting.

#### Airflow problem with Pipenv:

Since Airflow introduced a constraint file as the best practice to install it we
*might* face broken dependencies if we install Airflow using ``pipenv install``. The safe option
is that after installing default packages using standard Pipenv, we use ``pip`` inside Pipenv shell
and install Airflow in the [recommended way](https://airflow.apache.org/docs/apache-airflow/stable/installation/installing-from-pypi.html):

```bash
pipenv shell

(project) - pip install "apache-airflow[celery]==2.10.1" --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.10.1/constraints-3.8.txt"
```

Having said that, I
haven't faced any particular problem installing airflow using standard pipenv.

One recommended solution to *isolate* dependencies in Pipenv, is to use categories. So for example if I
install latest Airflow using this solution:
```bash
pipenv install --categories airflow "apache-airflow[celery]==2.10.1"
```
We'll get the following into the Pipfile:

```
[airflow]
apache-airflow = {extras = ["celery"], version = "==2.10.1"}
```

This might solve the problem. However, there are still packages that are NOT installed by default
using airflow that you might need later. Example is ``psycopg2-binary``.

If I install this package using standard pipenv, I'll get:

```
[packages]
...
psycopg2-binary = "*"
```

In Pipfile. However, in the Airflow constraint file ([latest](https://raw.githubusercontent.com/apache/airflow/constraints-2.10.1/constraints-3.8.txt)) the version is ``psycopg2-binary==2.9.9``. So this
poses a problem since Pipenv doesn't have a mechanism to constrain versions for specific upstream packages.

We might be able to solve the problem by using:
```bash
pipenv install --categories airflow "psycopg2-binary==2.9.9"
```

**But** We then have to manually check the conforming version of that library in the constraint
file of Airflow to the proper version.



### Use Sphinx!

All of the documents are written in Sphinx for now and they're by no means complete.
After the above very initial setup, compile the sphinx docs at the root project folder.

```bash
make -C docs html
```

Run:
```bash
google-chrome docs/build/html/index.html
```

Obviously, you can change ``google-chrome`` with the browser of your choice.