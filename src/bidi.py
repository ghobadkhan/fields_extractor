"""
Implements an improvised bidirectional communication object

Example

.. code-block:: python

    from bidi import Bidi
    b = Bidi(driver)

"""

__version__ = "0.1.0"

from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
import uuid

class Bidi:
    """Implements Bidirectional Communication

    With this object, we can inject a custom script to the webpage and get the
    raw results from a custom textbox
    :param driver: Instance of the selenium webdriver
    :type driver: WebDriver
    """
    def __init__(self,driver: WebDriver) -> None:
        self.driver = driver
        self.output_on = False
        self.output_node_id = self.generate_id()
        self.create_output_node()
        self.ids = set()

    @staticmethod
    def generate_id():
        """
        Generates universal ID for each injected script

        :return: UUID.
        :rtype: str
        """
        return str(uuid.uuid4())

    def inject_script(self,script):
        """
        Injects a custom script inside the active webpage
        After the script is created, the tag id is set to be an auto-generated
        UUID. The consumer must keep this UUID to remove it later

        :param script: JS script
        :type script: string
        :return: UUID of that script
        :rtype: str
        """
        script_element = """
            const script = document.createElement('script');
            script.innerHTML = `${arguments[0]}`;
            script.setAttribute('id',arguments[1])
            document.head.appendChild(script)
        """
        uid = self.generate_id()
        self.driver.execute_script(script_element,script,uid)
        return uid


    def create_output_node(self):
        """
        Creates a 'hidden' text area, so the output of script can be saved and
        picked up by the code.
        """
        script = f"""
            res = document.createElement('textarea')
            res.setAttribute('id','{self.output_node_id}')
            res.setAttribute('signal','free')
            res.style.display = 'none'
            document.body.appendChild(res)
        """
        self.driver.execute_script(script)
    
    def destroy_node(self,*ids):
        """
        Deletes scripts that are created previously.

        :param ids: A tuple of one or more UUIDs corresponding to the present scripts
        :type ids: tuple(str)
        """
        script = f"""
            el = document.getElementById(arguments[0])
            el.remove()
        """
        for id in ids:
            self.driver.execute_script(script,id)

    def get_raw_output(self):
        """
        Reads the content of the hidden text area and returns it

        :rtype: str
        """
        el = self.driver.find_element(By.ID,self.output_node_id)
        return el.get_attribute('innerHTML')