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
	def __init__(
			self,
			logger:Logger | None = None,
			disable_extension=True,
			headless=True,
			load_timeout=12,
			debug_address:str|None=None,
			driver_logging:bool = True,
			user_data_dir:str|None = None
			) -> None:
		self.driver_logging = driver_logging
		self.driver_options = {
			"disable_extension": disable_extension,
			"headless": headless,
			"load_timeout": load_timeout,
			"debug_address": debug_address,
			"user_data_dir": user_data_dir
		}
		self.driver = self.setup_webdriver(**self.driver_options)
		self.logger = logger if logger else getLogger()


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

	def take_screenshot(self,file_type:Literal["b64","png"]="b64"):
		img_file_name = f"{datetime.now().isoformat(timespec='seconds')}"
		folder = os.environ["SCREENSHOT_FOLDER"]
		match file_type:
			case "b64":
				img = self.driver.get_screenshot_as_base64()
				open(f"{folder}/{img_file_name}.b64","w").write(img)
			case "png":
				img = self.driver.get_screenshot_as_png()
				open(f"{folder}/{img_file_name}.png","wb").write(img)
			case _:
				self.logger.error(f"Invalid file_type chosen for screenshot ({file_type}).")
				return False
		self.logger.debug(f"Screenshot taken: {img_file_name}.{file_type}")
		return True
	
	def find_elements(self,value:str,by:Literal["ID","XPATH","CLASS"]="XPATH",just_one:bool=True):
		match by:
			case "ID":
				sby = By.ID
			case "XPATH":
				sby = By.XPATH
			case "CLASS":
				sby = By.CLASS_NAME
			case _:
				raise Exception("Unexpected 'by' value is entered")
		els = self.driver.find_elements(by=sby,value=value)
		if len(els) > 0:
			if just_one:
				return els[0]
			return els
		return None