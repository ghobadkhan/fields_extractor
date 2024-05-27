import dotenv
import os
import yaml
from logging import Logger, config, getLogger
from pathlib import Path
from src.db import DB
from src.contracts import JobData, Singleton
from src.driver import Driver
from dotenv import load_dotenv
from src.routines.myworkday import Routine
from selenium.webdriver import Keys, ActionChains
from time import sleep


# Dynamic Inputs
HEADLESS = True
LOAD_TIMEOUT = 50
USER_DATA_DIR = os.environ['CHROME_PROFILE']
dotenv.load_dotenv(".env")
logging_config_file_name = "src/logging_local.yml"
with open(logging_config_file_name, 'r') as logging_config_file:
    config.dictConfig(yaml.load(logging_config_file, Loader=yaml.FullLoader))

class Runner(metaclass=Singleton):
    _logger: Logger
    _job_data: JobData

    def __init__(self):
        # Load environment variables
        # Initialize logger config
        for folder in [
            os.environ["LOG_FOLDER"],
            os.environ["BACKUP_FOLDER"],
            os.environ["OUTPUT_FOLDER"]
            ]:
            Path(folder).mkdir(exist_ok=True)
        self._logger = getLogger("extract")
        # Initialize database
        self._job_data = DB(db_name=os.environ["DB_NAME"],output_folder=os.environ['OUTPUT_FOLDER'])
    

    def run_extractor(self):
        # self._logger.info("---------------- Start a new extraction process ----------------")
        # Initialize scrapper
        # self._logger.info("---------------- Extraction process finished successfully! ----------------")
        pass

    def test_run(self):
        load_dotenv()
        driver = Driver(load_timeout=-1, driver_logging=False,debug_address="localhost:9222")
        driver.driver.implicitly_wait(30)
        url = "https://td.wd3.myworkdayjobs.com/en-US/TD_Bank_Careers/job/Chilliwack%2C-British-Columbia/Customer-Experience-Associate-Future-Opportunities_R_1343945/apply/applyManually"
        driver.driver_get_link(url)
        routine = Routine(driver.driver)
        routine.run(url)

if __name__ == "__main__":
    runner = Runner()
        