import logging
import grpc
import os
from concurrent.futures import ThreadPoolExecutor
from functools import wraps

from .build import interface_pb2_grpc as pb2_grpc
from .build import interface_pb2 as pb2
from .service import WebdriverService, logger


# In case GRPC_PORT is not set in .env
FALLBACK_GRPC_PORT = "43321"

def webdriver_client(func):
	channel = grpc.insecure_channel(f"localhost:{os.environ['GRPC_PORT']}")
	@wraps(func)
	def wrapper(*args, **kwargs):
		with channel:
			stub = pb2_grpc.WebDriverStub(channel=channel)
			return func(*args,**kwargs, stub=stub)
	return wrapper

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
	logging.basicConfig(level=logging.INFO)
	serve()