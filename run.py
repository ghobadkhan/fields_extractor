from typing import Tuple
import dotenv
import os
import yaml
from logging import Logger, config, getLogger
from pathlib import Path
from src.bidi import Bidi
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
	_driver: Driver
	_bidi: Bidi

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
		# Initialize webdriver
		self._driver = Driver(load_timeout=-1, driver_logging=False,debug_address="localhost:9222")
	

	def run_extractor(self):
		# self._logger.info("---------------- Start a new extraction process ----------------")
		# Initialize scrapper
		# self._logger.info("---------------- Extraction process finished successfully! ----------------")
		pass

	def test_fill_form(self):
		load_dotenv()
		# driver.driver.implicitly_wait(10)
		routine = Routine(self._driver.driver,
				"https://td.wd3.myworkdayjobs.com/en-US/TD_Bank_Careers/job/Toronto%2C-Ontario/Sr-Software-Engineer--ETrading--ION_R_1346079/apply/applyManually")
		(
			routine
			.goto_url().pause(2).sign_in().pause(3).refresh()
			.pause(5).my_information().pause(1)
			.submit_or_next().pause(5).my_experience()
		)
		routine.submit_or_next().pause(5).my_experience(selected_sections=["files"])

	def test_observe_page_mutation(self):
		load_dotenv()
		self._bidi = Bidi(self._driver.driver)

		# Inject a mutation observer script
		script = """
            const callback = (mutationList, observer) => {
                for (const mutation of mutationList) {
                        if (mutation.type === 'childList') {
                            console.log('A child node has been added or removed: '+ mutation.addedNodes[0]);
                            if (mutation.addedNodes.length > 0 && mutation.addedNodes[0].innerText){
                                res = document.getElementById('%s')
                                res.innerHTML = mutation.addedNodes[0].innerText
                        }
                    }
                }
            };
            const observer = new MutationObserver(callback);
        """ %(self._bidi.output_node_id)
		observer_uid = self._bidi.inject_script(script)

		# Start The mutation observer script
		target = "body"
		script = """
            const targetNode = document.getElementsByTagName('%s');
            const config = { attributes: true, childList: true, subtree: true };
            // Start observing the target node for configured mutations
            observer.observe(targetNode[0], config);
        """ % (target)
		starter_uid = self._bidi.inject_script(script)
		return observer_uid, starter_uid

	def test_stop_page_mutation_observer(self,ids:Tuple[str]):
		assert self._bidi
		uid = self._bidi.inject_script("observer.disconnect()")
		self._bidi.destroy_node(uid,*ids)


if __name__ == "__main__":
	runner = Runner()
		