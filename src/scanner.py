import os
from typing import List, Literal
from dotenv import load_dotenv
from .driver import Driver
from .routines.myworkday import Routine
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver import Keys, ActionChains
from time import sleep

class ScannerParent:
    input_type_mapping = {
        "text": ('xpath',"self::input[contains(@type,'text')]"),
        "radio": ('xpath',"self::input[contains(@type,'radio')]"),
        "checkbox": ('xpath',"self::input[contains(@type,'checkbox')]")
    }

    def __init__(self, driver:WebDriver) -> None:
        self.driver = driver
        self.wait = WebDriverWait(driver=driver,timeout=10,poll_frequency=1)

    """Regular xpath element search"""
    @staticmethod 
    def xpath_condition(el:WebElement,predicate:str):
        try:
            el.find_element("xpath",predicate)
            return True
        except:
            return False
    
    """Case insensitive attribute value search
    """
    @staticmethod
    def case_in(el:WebElement,predicate:str,attr:str,value:str):
        elements = el.find_elements('xpath',predicate)
        for element in elements:
            if element.get_attribute(attr).lower().find(value) != -1:
                return True
        else:
            return False

    @staticmethod
    def take_screenshot(el:WebElement,img_file_name:str,file_type:Literal["b64","png"]="png"):
        folder = os.environ["SCREENSHOT_FOLDER"]
        match file_type:
            case "b64":
                img = el.screenshot_as_base64
                open(f"{folder}/{img_file_name}.b64","w").write(img)
            case "png":
                img = el.screenshot_as_png
                open(f"{folder}/{img_file_name}.png","wb").write(img)
            case _:
                return False
        return True

class Scanner(ScannerParent):
    def __init__(self,driver:WebDriver,form_xpath:str) -> None:
        self.form_predicate = form_xpath
        self.override_input_type_mapping({
            # Contains an ancestor that has the required data-automation-id value
            "dropdown": ("xpath","self::button[contains(@aria-haspopup,'listbox')]"),
            "multiselect_input": ("case_in","ancestor::*[@data-automation-id]",'data-automation-id','multiselect'),
        })
        super().__init__(driver)

    def override_input_type_mapping(self,mapping:dict):
        for i_type,definition in mapping.items():
            self.input_type_mapping[i_type] = definition
    
    def condition_true(self,el:WebElement,condition:List[str]):
        match condition[0]:
            case 'xpath':
                return self.xpath_condition(el,*condition[1:])
            case 'case_in':
                return self.case_in(el,*condition[1:])
            case _:
                raise Exception(f"Unexpected condition function '{condition[0]}'")
        
    def find_input_type(self,el:WebElement):
        for i_type, condition in self.input_type_mapping.items():
            if self.condition_true(el,condition):
                return i_type
        return "unknown"
    
    def run(self):
        self.driver.refresh()
        self.wait.until(ec.presence_of_element_located(("xpath",self.form_predicate)))
        chain = ActionChains(self.driver)
        while self.is_in(self.driver.switch_to.active_element,"body"):
            chain.send_keys(Keys.TAB).perform()
            el = self.driver.switch_to.active_element
            if self.is_in(el,self.form_predicate):
                print(el.tag_name,self.find_input_type(el))
                # self.take_screenshot(el,f"{i}-{el.tag_name}")
            sleep(0.2)
    
    def is_in(self,p:WebElement,xpath:str):
        try:
            p.find_element("xpath",f"ancestor::{xpath}")
            return True
        except:
            return False


if __name__ == "__main__":
    load_dotenv()
    driver = Driver(load_timeout=-1, driver_logging=False,debug_address="localhost:9222")
    routine = Routine(driver.driver,"https://td.wd3.myworkdayjobs.com/en-US/TD_Bank_Careers/login?redirect=%2Fen-US%2FTD_Bank_Careers%2Fjob%2FMarkham%252C-Ontario%2FContact-Centre-Representative--Canadian-Banking--Easyline_R_1342984%2Fapply%2FapplyManually")
    scanner = Scanner(driver.driver,"//div[contains(@data-automation-id,'Page')]")
    scanner.run()