"""
### First Airflow TaskFlow to fill forms

This will get bigger and better as I learn

    Also, this is from my under-developed algorithm. Please forgive me
"""

from __future__ import annotations

import datetime
import pendulum
import logging
from time import sleep
from typing import TYPE_CHECKING, Optional

from airflow.decorators import task
from airflow.models.dag import DAG
from airflow.models.param import Param
from airflow.utils.trigger_rule import TriggerRule
from airflow.sensors.external_task import ExternalTaskMarker, ExternalTaskSensor
from airflow.models.dagrun import DagRun
from airflow.models.taskinstance import TaskInstance

from driver import Driver
# from .myworkday import Routine    

logger = logging.getLogger("airflow.task")

# routine = Routine(
#     driver.driver,
#     "https://td.wd3.myworkdayjobs.com/en-US/TD_Bank_Careers/job/Toronto%2C-Ontario/Sr-Software-Engineer--ETrading--ION_R_1346079/apply/applyManually")

dw = Driver.singleton(load_timeout=-1, headless=False,driver_logging=False)
with DAG(
    dag_id="form_fill_dag_1",
    dag_display_name="Fill the webforms!",
    description="This is (still) a test",
    doc_md=__doc__,
    schedule="@once",
    start_date=pendulum.now(),
    catchup=False,
    tags=["fields_extractor", "arian"],
    # params={
    #     "current_line": Param(default=-1,type="integer",readOnly=True),
    #     "payload": Param("Say Something",type="string"),
    #     "test":"hello"
    # }
) as dag:
    
    
    @task()
    def get_url():
        dw.driver_get_link("https://www.google.com")
    
    @task()
    def refresh():
        dw.driver.refresh()

    @task()
    def close():
        dw.driver.close()

    get_url() >> refresh() >> close()


if __name__ == "__main__":
    dag.test()