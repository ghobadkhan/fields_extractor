Installation and Initialization
===============================

Development
-----------

Environment Variables:
++++++++++++++++++++++

The project uses a ``.env`` file at the root directory to set all of the related
environment variables. this file is not included in the repository by default
but an example is added at ``./src/.env.example`` after cloning from the
repository, the next step should be copying and renaming this file to the root
folder.


Package Management
++++++++++++++++++

The project uses `Pipenv <https://pipenv.pypa.io/en/latest/>`_ as package manager. There are many
advantages in using Pipenv not least of them is that ``.env`` variables are loaded by default.

*Important* Before proceeding further, make sure you have created ``.env`` and set the corresponding
values correctly.

If you haven't installed Pipenv globally, first install it using:

.. code-block:: bash

    pip3 install --user pipenv

Then in the project root folder run:

.. code-block:: bash

    pipenv sync

This should read Pipfile, install dependencies and update the lock file accordingly.

*Note*: To switch to Pipenv virtual env, use ``pipenv shell``. 
Also, to add packages and dependencies always use Pipenv's commands, e.g. ``pipenv install <package>``.


AirFlow
+++++++

This project uses `AirFlow <https://airflow.apache.org/>`_ for task management and pipelining. My paradigm is to use all of the required
tools in a completely isolated environment, so the following are the steps to install and run AirFlow
in the virtual environment, created by ``Pipenv``:

1. Make sure that you have correctly set the following variables in ``.env`` and
   created the corresponding folders:

   a. ``AIRFLOW_HOME="path/to/airflow/home"``
   b. ``AIRFLOW__CORE__DAGS_FOLDER="path/to/project/dags/folder"``

.. 
    (Above) You need 3 spaces before a nested item, not a tab!
..

2. Switch to pipenv venv using ``pipenv shell``.

3. Use the standard installation procedure as mentioned in the AirFlow
   `documentation
   <https://airflow.apache.org/docs/apache-airflow/stable/installation/installing-from-pypi.html>`_::

    # Always consult with the documentation for the latest version!
    pip install "apache-airflow[celery]==2.9.3" --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.9.3/constraints-3.8.txt"

4. Run ``airflow`` in the venv to initialize AirFlow.