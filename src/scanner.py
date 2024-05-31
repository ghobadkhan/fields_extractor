import os
import re
from typing import List, Literal
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver import Keys, ActionChains
from time import sleep

class ScannerParent:
    question_pattern = re.compile(r".{4,}\?.*")
    input_type_mapping = {
        "text": ('xpath',"self::input[@type='text']"),
        "radio": ('xpath',"self::input[@type='radio']"),
        "checkbox": ('xpath',"self::input[@type='checkbox']"),
        "textarea": ('xpath',"self::textarea"),
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
        self.chain = ActionChains(driver)
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
    
    def active_element(self) -> WebElement:
        return self.driver.switch_to.active_element
    
    def press_key(self,key=Keys.TAB):
        self.chain.send_keys(key).perform()
        # print(f"pressed {key}")

    def press_shift_tab(self):
        self.chain.key_down(Keys.SHIFT).send_keys(Keys.TAB).perform()
        # print("pressed shift-tab")
    

    def refresh_for_form(self):
        self.driver.refresh()
        self.wait.until(ec.presence_of_element_located(("xpath","//"+self.form_predicate)))
    
    def form_elements(self):
        while not self.is_in(self.active_element(),"body"):
            print("not in body yet")
            self.press_key()
        while self.is_in(self.active_element(),"body"):
            self.press_key()
            if self.is_in(self.active_element(),self.form_predicate):
                yield self.active_element()
                # self.take_screenshot(el,f"{i}-{el.tag_name}")
            sleep(0.2)

    def find_text(self,el:WebElement):
        id = el.get_attribute("id")
        for e in self.driver.find_elements("xpath",f"//*[@for='{id}']"):
            if e.text != "":
                return e.text
        
    def find_radio_text(self,first_radio:WebElement):
        # Find all preceding elements that contain a text and that text matches the question pattern
        possible_text = [e.text for e in first_radio.find_elements("xpath","preceding::*[text()]") if self.question_pattern.match(e.text)]
        if len(possible_text) > 0:
            # Since preceding elements for closest in the last [farthest,....,closest],
            # the last one is the possible related legend
            text = possible_text[-1]
        else:
            #TODO: replace this with log or exception
            text = None
            print("Warning, no legend found for the radio group.")

        # Each radio input can be selected with arrow keys...
        choices = [{
            "element": first_radio,
            "text": self.find_text(first_radio)
        }]
        self.press_key(Keys.ARROW_DOWN)
        while self.active_element() != first_radio:
            choices.append({
                "element": self.active_element(),
                "text": self.find_text(self.active_element())
            })
            self.press_key(Keys.ARROW_DOWN)
            sleep(0.2)
        return text, choices
    
    def find_checkbox_text(self,first_checkbox:WebElement):
        """
        First we assume that checkbox is grouped so we look for the group text.
        The we'll check if more checkboxes are following the current checkbox (first_checkbox).
        If we find more, we bunch them up and att the text as their group text
        Else, we only return the info of the first_checkbox
        """

        # Find all preceding elements that contain a text and that text matches the question pattern
        possible_text = [e.text for e in first_checkbox.find_elements("xpath","preceding::*[text()]") if self.question_pattern.match(e.text)]
        if len(possible_text) > 0:
            # Since preceding elements for closest in the last [farthest,....,closest],
            # the last one is the possible related legend
            text = possible_text[-1]
        else:
            #TODO: replace this with log or exception
            text = None
            print("Warning, no legend found for the radio group.")
        choices = [{
            "element": first_checkbox,
            "text": self.find_text(first_checkbox)
        }]
        self.press_key()
        while self.find_input_type(self.active_element()) == "checkbox":
            choices.append({
                "element": self.active_element(),
                "text": self.find_text(self.active_element())
            })
            self.press_key()
        # For some reason, if the last element is not check box, we don't
        # need to revert to element before.
        # self.press_shift_tab()
        if len(choices) > 1:
            # We have a group of checkboxes
            return text, choices
        else:
            # We only one checkbox
            return None, choices[0]
        
    def find_dropdown_text(self):
        #TODO: Still under testing and must be updated. Very slow
        choices = set()
        for key in [Keys.ARROW_DOWN, Keys.ARROW_UP]:
            for _ in range(5):
                sleep(0.5)
                self.active_element().click()
                sleep(0.3)
                self.press_key(key)
                sleep(0.2)
                self.press_key(Keys.ENTER)
                sleep(0.2)
                choices.add(self.active_element().text)

        return list(choices)
    
    def reset_dropdown(self):
        # TEMP: This is for testing of workday element only and temporary
        inp = self.active_element().find_element("xpath","following::input")
        self.driver.execute_script("arguments[0].removeAttribute('value')",inp)
        self.driver.execute_script("arguments[0].innerText='select one'",self.active_element())


    def focus(self, el:WebElement):
        """Return focus to specific element
        """
        self.driver.execute_script("arguments[0].focus()",el)
    

        
    def is_in(self,p:WebElement,xpath:str):
        try:
            p.find_element("xpath",f"ancestor::{xpath}")
            return True
        except:
            return False


if __name__ == "__main__":
    ...