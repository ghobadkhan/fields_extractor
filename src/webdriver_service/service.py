"""
#### Example of a gRPC server client:


```python

import os
import grpc
from time import sleep
from src.webdriver_service.build import interface_pb2 as pb2
from src.webdriver_service.build import interface_pb2_grpc as pb2_grpc
from src.webdriver_service.dataclasses import DriverOptions

with grpc.insecure_channel(f"localhost:{os.environ['GRPC_PORT']}") as channel:
    stub = pb2_grpc.WebDriverStub(channel=channel)
    options = DriverOptions(headless=False, load_timeout=12).to_message()
    response:pb2.ServiceResponse = stub.start_driver(options)
    print(response.status, response.message)
    sleep(5)
    response:pb2.ServiceResponse = stub.get_url(pb2.URL(url="https://www.google.com"))
    print(response.status, response.message)

```
"""

from __future__ import annotations
from datetime import datetime
import logging
import os
from time import sleep
import grpc

from typing import Callable, Literal, Optional, Tuple, Union
from functools import wraps
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import Keys, ActionChains, Chrome, ChromeService
from google.protobuf.struct_pb2 import Struct

from .build import interface_pb2 as pb2
from .build.interface_pb2_grpc import WebDriverServicer
from src.webdriver_service import interface

logger = logging.getLogger(__name__)


def catch(message: str|None = None):
	def decorator(func:Callable):
		@wraps(func)
		def wrapper(*args,**kwargs):
			try:
				return func(*args,**kwargs)
			except Exception as e:
				return pb2.ServiceResponse(
					status=pb2.StatusType.STATUS_FAILURE,
					message=message,
					exception=str(e)
				)
		return wrapper
	return decorator


class WebdriverService(WebDriverServicer):
	
	@catch(message="Couldn't start the webdriver.")
	def start_driver(self, request: pb2.DriverOptions, context):
		driver_options = interface.DriverOptions.from_message(request)
		self._driver = self._setup_webdriver(driver_options)
		return pb2.ServiceResponse(status=pb2.StatusType.STATUS_OK)

	@catch(message="Couldn't get the url.")
	def get_url(self, request: pb2.WebdriverRequest, context):
		self.driver.get(request.url)
		return pb2.ServiceResponse(status=pb2.StatusType.STATUS_OK)
	
	@catch(message="Couldn't refresh.")
	def refresh(self, request: pb2.Empty, context):
		self.driver.refresh()
		return pb2.ServiceResponse(status=pb2.StatusType.STATUS_OK)
	
	@catch(message="Sign in failure!")
	def sign_in(self, request: pb2.Credentials, context):
		credentials = interface.Credentials.from_message(request)
		self._perform_sign_in(credentials)
		return pb2.ServiceResponse(status=pb2.StatusType.STATUS_OK)

	
	@catch(message="Webdriver stop failed.")
	def stop_driver(self, request: pb2.Empty, context):
		self.driver.quit()
		del self._driver
		return pb2.ServiceResponse(status=pb2.StatusType.STATUS_OK)
	
	@catch(message="Screenshot failed.")
	def take_screenshot(self, request: pb2.Empty, context):
		img,name = self._take_screenshot()
		response = interface.ServiceResponse(
			status=interface.StatusType.STATUS_OK,
			payload=interface.Payload(images={
				name:img
			})
		)
		return response.to_message()


	@property
	def driver(self) -> Chrome:
		if not hasattr(self,"_driver") or not self._driver:
			raise ValueError("Webdriver is not initialized")
		return self._driver

	def _setup_webdriver(self,ops:interface.DriverOptions):
		#TODO: Load options from a file or other external source
		webdriver_options = Options()
		if ops.debug_address is None:
			if ops.user_data_dir is not None:
				webdriver_options.add_argument(f"user-data-dir={ops.user_data_dir}")
			webdriver_options.add_argument("disable-infobars")
			# Don't enable the extension for crawling from linkedin. We'll use the extension later
			# for auto-fill (hopefully)
			if ops.disable_extension:
				webdriver_options.add_argument("--disable-extensions")
			if ops.headless:
				webdriver_options.add_argument("--headless")
		else:
			# Example: google-chrome --remote-debugging-port=9222 --remote-allow-origins=*
			webdriver_options.add_experimental_option("debuggerAddress", ops.debug_address)
		if ops.driver_logging:
			service = ChromeService(log_output=f"{os.environ['LOG_FOLDER']}/chrome.log")
		else:
			service = None
		driver = Chrome(options=webdriver_options,service=service) #type: ignore
		if ops.load_timeout > 0:
			driver.set_page_load_timeout(ops.load_timeout)
		return driver
	
	def _perform_sign_in(self, creds:interface.Credentials):
			sign_in_form = self.driver.find_element("xpath","//form[contains(@data-automation-id,'signInFormo')]")
			labels = sign_in_form.find_elements("xpath",".//label")
			for label in labels:
				id = label.get_dom_attribute("for")
				text = label.text.lower()
				inp = sign_in_form.find_element("xpath",f".//input[contains(@id,'{id}')]")
				if text.find("email") != -1:
					inp.send_keys(creds.username)
				elif text.find("password") != -1:
					inp.send_keys(creds.password)
				else:
					raise Exception(f"Error signing in, got an unexpected field: {text}")
				sleep(0.5)
			btn = sign_in_form.find_element("xpath",".//div[contains(@data-automation-id,'click_filter')]")
			ActionChains(self.driver).move_to_element(btn).pause(0.5).send_keys(Keys.ENTER).pause(0.5).click().perform()


	def _take_screenshot(self,file_type:Literal["b64","png"]="png", save=False
					) -> Tuple[bytes,str]:
		
		img_file_name = f"scrshot-{datetime.now().isoformat(timespec='seconds')}"
		folder = os.environ["SCREENSHOT_FOLDER"]
		match file_type:
			case "b64":
				img = self.driver.get_screenshot_as_base64()
				if save:
					open(f"{folder}/{img_file_name}.b64","w").write(img)
				img = img.encode()
			case "png":
				img = self.driver.get_screenshot_as_png()
				if save:
					open(f"{folder}/{img_file_name}.png","wb").write(img)
			case _:
				raise ValueError(f"Invalid file_type chosen for screenshot ({file_type}).")
		logger.debug(f"Screenshot taken: {img_file_name}.{file_type}")
		return img, img_file_name
	

