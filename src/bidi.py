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
        script = f"""
            res = document.createElement('textarea')
            res.setAttribute('id','{self.output_node_id}')
            res.setAttribute('signal','free')
            res.style.display = 'none'
            document.body.appendChild(res)
        """
        self.driver.execute_script(script)
    
    def destroy_node(self,*ids):
        script = f"""
            el = document.getElementById(arguments[0])
            el.remove()
        """
        for id in ids:
            self.driver.execute_script(script,id)

    def create_mutation_observer(self):
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
        """ %(self.output_node_id)
        uid = self.inject_script(script)
        # self.driver.execute_script(script,self.output_node_id)
        return uid
        

    def start_mutation_observer(self,target:str="body"):
        script = """
            const targetNode = document.getElementsByTagName('%s');
            const config = { attributes: true, childList: true, subtree: true };
            // Start observing the target node for configured mutations
            observer.observe(targetNode[0], config);
        """ % (target)
        uid = self.inject_script(script)
        return uid

    def get_raw_output(self):
        el = self.driver.find_element(By.ID,self.output_node_id)
        return el.get_attribute('innerHTML')