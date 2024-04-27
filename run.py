import sys
import dotenv
import os
import yaml
from logging import Logger, config, getLogger
from pathlib import Path
from src.db import DB
from src.contracts import JobData, Singleton


# Dynamic Inputs
HEADLESS = True
LOAD_TIMEOUT = 50
USER_DATA_DIR = os.environ['CHROME_PROFILE']


class Runner(metaclass=Singleton):
    _logger: Logger
    _job_data: JobData

    def __init__(self):
        # Load environment variables
        dotenv.load_dotenv(".env")
        # Initialize logger config
        for folder in [
            os.environ["LOG_FOLDER"],
            os.environ["BACKUP_FOLDER"],
            os.environ["OUTPUT_FOLDER"]
            ]:
            Path(folder).mkdir(exist_ok=True)
        logging_config_file_name = "src/logging_local.yml"
        with open(logging_config_file_name, 'r') as logging_config_file:
            config.dictConfig(yaml.load(logging_config_file, Loader=yaml.FullLoader))
        self._logger = getLogger("extract")
        # Initialize database
        self._job_data = DB(db_name=os.environ["DB_NAME"],output_folder=os.environ['OUTPUT_FOLDER'])
    

    def run_extractor(self):
        # self._logger.info("---------------- Start a new extraction process ----------------")
        # Initialize scrapper
        # self._logger.info("---------------- Extraction process finished successfully! ----------------")
        pass


if __name__ == "__main__":
    runner = Runner()
        