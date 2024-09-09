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
import logging
import os
import grpc

from typing import Callable
from functools import wraps
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options
from concurrent.futures import ThreadPoolExecutor

from .build import interface_pb2 as pb2
from .build import interface_pb2_grpc as pb2_grpc
from src.webdriver_service.dataclasses import DriverOptions

logger = logging.getLogger(__name__)

# In case GRPC_PORT is not set in .env
FALLBACK_GRPC_PORT = "43321"

def catch(message: str|None = None):
	def decorator(func:Callable):
		@wraps(func)
		def wrapper(*args,**kwargs):
			try:
				return func(*args,**kwargs)
			except Exception as e:
				return pb2.ServiceResponse(
					status=pb2.ServiceResponse.STATUS_FAILURE,
					message=message,
					exception=e.args[0]
				)
		return wrapper
	return decorator


class WebdriverService(pb2_grpc.WebDriverServicer):
	
	@catch(message="Couldn't start the webdriver.")
	def start_driver(self, request: pb2.DriverOptions, context):
		driver_options = DriverOptions.from_message(request)
		self._driver = self._setup_webdriver(driver_options)
		return pb2.ServiceResponse(status=pb2.ServiceResponse.STATUS_OK)

	@catch(message="Couldn't get the url.")
	def get_url(self, request: pb2.URL, context):
		self.driver.get(request.url)
		return pb2.ServiceResponse(status=pb2.ServiceResponse.STATUS_OK)
	
	@catch(message="Couldn't refresh.")
	def refresh(self, request: pb2.Empty, context):
		self.driver.refresh()
		return pb2.ServiceResponse(status=pb2.ServiceResponse.STATUS_OK)
	
	@catch(message="Webdriver stop failed.")
	def stop_driver(self, request: pb2.Empty, context):
		self.driver.quit()
		del self._driver
		return pb2.ServiceResponse(status=pb2.ServiceResponse.STATUS_OK)


	@property
	def driver(self) -> webdriver.Chrome:
		if not hasattr(self,"_driver") or not self._driver:
			raise ValueError("Webdriver is not initialized")
		return self._driver

	def _setup_webdriver(self,ops:DriverOptions):
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
			service = webdriver.ChromeService(log_output=f"{os.environ['LOG_FOLDER']}/chrome.log")
		else:
			service = None
		driver = webdriver.Chrome(options=webdriver_options,service=service) #type: ignore
		if ops.load_timeout > 0:
			driver.set_page_load_timeout(ops.load_timeout)
		return driver
	
def serve():
	
	server=grpc.server(ThreadPoolExecutor(max_workers=5))
	pb2_grpc.add_WebDriverServicer_to_server(WebdriverService(),server)
	port = os.environ.get("GRPC_PORT")
	if port is None:
		port = FALLBACK_GRPC_PORT
		logger.warning(f"GRPC_PORT is not set in .env, falling back to default: {port}")
		os.environ["GRPC_PORT"] = port

	server.add_insecure_port("[::]:"+port)
	server.start()
	logger.info("Server Started")
	server.wait_for_termination()

if __name__ == "__main__":
	logging.basicConfig(level=logging.DEBUG)
	serve()
