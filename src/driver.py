"""
Contains wrapper class from selenium webdriver
"""

import re
import os
from typing import Literal
from pathlib import Path
from logging import Logger, getLogger
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options
from datetime import datetime

extract_number_pattern = re.compile(r"\D*(\d*)\D*")

class Driver():
	"""
	A wrapper class that sets up the selenium webdriver with desired options and
	some helper functions for routine tasks (such as taking screenshots)

	:param logger: Instance of python's Logger object
	:type logger: Logger
	:param debug_address: Is in the form of host:port
	:type debug_address: str
	"""
	def __init__(
			self,
			logger:Logger | None = None,
			disable_extension=True,
			headless=True,
			load_timeout=12,
			debug_address:str|None=None,
			driver_logging:bool = True,
			user_data_dir:str|None = None
			):

		self.driver_logging = driver_logging
		self.driver_options = {
			"disable_extension": disable_extension,
			"headless": headless,
			"load_timeout": load_timeout,
			"debug_address": debug_address,
			"user_data_dir": user_data_dir
		}
		self.logger = logger if logger else getLogger()
		return self.setup_webdriver(**self.driver_options)


	def re_init_driver(self):
		self.logger.debug("Re-Initializing the webdriver.")
		self.driver.quit()
		self.driver = self.setup_webdriver(**self.driver_options)

	def setup_webdriver(
			self,
			disable_extension=True,
			headless=True,
			load_timeout=12,
			debug_address:str|None=None,
			user_data_dir:str|None=None
		):
		#TODO: Load options from a file or other external source
		options = Options()
		if debug_address is None:
			if user_data_dir is not None:
				options.add_argument(f"user-data-dir={user_data_dir}")
			options.add_argument("disable-infobars")
			# Don't enable the extension for crawling from linkedin. We'll use the extension later
			# for auto-fill (hopefully)
			if disable_extension:
				options.add_argument("--disable-extensions")
			if headless:
				options.add_argument("--headless")
		else:
			# Example: google-chrome --remote-debugging-port=9222 --remote-allow-origins=*
			options.add_experimental_option("debuggerAddress", debug_address)
		if self.driver_logging:
			service = webdriver.ChromeService(log_output=f"{os.environ['LOG_FOLDER']}/chrome.log")
		else:
			service = None
		driver = webdriver.Chrome(options=options,service=service) #type: ignore
		if load_timeout > 0:
			driver.set_page_load_timeout(load_timeout)
		return driver

	def driver_get_link(self, link:str):
		self.logger.debug(f"Get URL: {link}")
		try:
			self.driver.get(link)
			return True
		except TimeoutException:
			self.logger.warning("Page load timed out!")
			return True
		except WebDriverException as e:
			if e.msg is not None and (e.msg.find("ERR_INTERNET_DISCONNECTED") != -1 or \
			e.msg.find("ERR_PROXY_CONNECTION_FAILED") != -1):
				raise Exception("RETRY","Connecting Internet")
			else:
				raise Exception("Webdriver Exception:",e.msg)