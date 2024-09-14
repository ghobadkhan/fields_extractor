import os
from time import sleep
from src.webdriver_service import client
from src.webdriver_service.build import interface_pb2_grpc as pb2_grpc
from src.webdriver_service import interface

@client()
def start_driver(stub:pb2_grpc.WebDriverStub|None=None):
    assert stub
    options = interface.DriverOptions(
        headless=False,
        disable_extension=True,
        user_data_dir= os.environ["CHROME_PROFILE"]
    )
    resp = stub.start_driver(options.to_message())
    return interface.ServiceResponse.from_message(resp)

@client()
def get_url(url:str,stub:pb2_grpc.WebDriverStub|None=None):
    assert stub
    request = interface.WebdriverRequest(
        url=url
    )
    resp = stub.get_url(request.to_message())
    return interface.ServiceResponse.from_message(resp)


@client()
def screenshot(stub:pb2_grpc.WebDriverStub|None=None):
    assert stub
    response_pb2 = stub.take_screenshot(interface.Empty().to_message())
    response = interface.ServiceResponse.from_message(response_pb2)
    if response.payload and response.payload.images:
        for name,img in response.payload.images.items():
            with open(f"{name}.png","wb") as f:
                f.write(img)
    return response

@client()
def quit(stub:pb2_grpc.WebDriverStub|None=None):
    assert stub
    resp = stub.stop_driver(interface.Empty().to_message())
    return interface.ServiceResponse.from_message(resp)
    

if __name__ == "__main__":
    start_driver()
    sleep(1)
    get_url(url="https://www.yahoo.com")
    sleep(2)
    screenshot()
    sleep(1)
    quit()

