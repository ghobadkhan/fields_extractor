"""
So far this is only tested for TD: https://td.wd3.myworkdayjobs.com/
"""
from typing import Any, Dict, List
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver import Keys, ActionChains
from time import sleep
import json
import re

class Routine:
    base_url_pattern = re.compile(r"https?:\/\/(.*\.)?(.*\..*?)\/.*")

    def __init__(self, driver: WebDriver,url:str, def_address:str="db/experience_definitions.json") -> None:
        self.driver = driver
        self.current_element: WebElement|None = None
        self.url = url
        self.base_url = self.base_url_pattern.findall(self.url)[0][-1]
        self.my_information_fields = {
            "formField-sourcePrompt": lambda el: self._fill_multi_select_container(el,"formField-sourcePrompt","a"),
            "formField-":lambda el: self._select_radio_button(el,"No"),
            "formField-countryDropdown":None,
            "formField-legalNameSection_firstName":lambda el: self._fill_simple_text_input(el,"Ahamad"),
            "formField-legalNameSection_lastName":lambda el: self._fill_simple_text_input(el,"Noori"),
            "formField-formField-preferredNameCheckbox":None,
            "formField-addressSection_addressLine1":lambda el: self._fill_simple_text_input(el,"Your Mama's Home"),
            "formField-addressSection_city":lambda el: self._fill_simple_text_input(el,"Toronto"),
            "formField-addressSection_countryRegion":lambda el: self._select_dropdown(el,"Ontario"),
            "formField-addressSection_postalCode":lambda el: self._fill_simple_text_input(el,"M2M 1E1"),
            "formField-email":None,
            "formField-phone-device-type":None,
            "formField-country-phone-code":None,
            "formField-phone-number":lambda el: self._fill_simple_text_input(el,"4166969699"),
            "formField-phone-extension":None
        }
        self.definitions = json.load(open(def_address))
        

    # ****** Actions *******

    def goto_url(self):
        self.driver.get(self.url)
        return self

    def get_creds(self):
        assert self.base_url
        with open("db/creds.csv","r") as f:
            f.readline()
            for line in f:
                fields = line.rstrip().split(",")
                if fields[0].find(self.base_url) != -1:
                    self.usr, self.passwd = fields[1:]
                    return self
        raise Exception(f"Could not find user and password for base url: {self.base_url}")
    
    def pause(self,duration:float=1):
        sleep(duration)
        return self
    
    def refresh(self):
        self.driver.refresh()
        return self
    
    def sign_in(self):
        self._perform_sign_in(self.usr,self.passwd)
        return self
    
    def my_information(self):
        self._fill_my_information()
        return self
    
    def find_click_submit_btn(self):
        self._find_submit_or_next_btn().click()
        return self
    
    def my_experience(self,selected_sections:list|None=None):
        self._fill_my_experience(selected_sections=selected_sections)
        return self
    
    # ****** End of Actions *******
        
    # def run(self, url:str):
        # current_page = self.get_progress()['current']
        # match current_page:
        #     case "My Information":
        #         self.my_information()
        #     case "My Experience":
        #         self.my_experience()

    

    # *** Fill Pages ***
    def _perform_sign_in(self,user:str, password:str):
        sign_in_form = self.driver.find_element("xpath","//form[contains(@data-automation-id,'signInFormo')]")
        labels = sign_in_form.find_elements("xpath",".//label")
        for label in labels:
            id = label.get_dom_attribute("for")
            text = label.text.lower()
            inp = sign_in_form.find_element("xpath",f".//input[contains(@id,'{id}')]")
            if text.find("email") != -1:
                inp.send_keys(user)
            elif text.find("password") != -1:
                inp.send_keys(password)
            else:
                raise Exception(f"Error signing in, got unexpected field: {text}")
            sleep(0.5)
        btn = sign_in_form.find_element("xpath",".//div[contains(@data-automation-id,'click_filter')]")
        ActionChains(self.driver).move_to_element(btn).pause(0.5).send_keys(Keys.ENTER).pause(0.5).click().perform()

    def _fill_my_information(self):
        #TODO: This must be integrated with the definitions json framework later 
        f_list = self.driver.find_elements("xpath","//div[contains(@data-automation-id,'formField')]")
        print(f_list)
        for f in f_list:
            func = self.my_information_fields.get(f.get_attribute('data-automation-id')) # type: ignore
            if func is not None:
                try:
                    func(f)
                except Exception as e:
                    print(f"Error for {f.get_attribute('data-automation-id')}")
                    print(e)
                sleep(1)

    def _find_submit_or_next_btn(self):
        pattern = re.compile(r".*save|next|done|submit.*",re.IGNORECASE)
        btns = self.driver.find_elements("xpath","//button")
        for btn in btns:
            if pattern.match(btn.text):
                return btn
        raise Exception("Submit button not found")


    # *** End Fill Pages ***

    def _fill_multi_select_container(self,el:WebElement,data_automation_id:str, value:str):
        container = el.find_element(by="xpath",value=".//*[contains(@data-automation-id,'multiselectInputContainer')]")
        match data_automation_id:
            case "formField-sourcePrompt":
                container.click()
                sleep(3)
                search_box = container.find_element(by="xpath",value=".//*[contains(@data-automation-id,'searchBox')]")
                search_box.send_keys(value)
                search_box.send_keys(Keys.ENTER)
                sleep(1)
                container.find_element(by="xpath",value="//div[contains(@data-automation-id,'promptLeafNode')]").click()


    def _select_radio_button(self,el:WebElement, value:str):
        radio_label = el.find_element(by="xpath",value=f".//label[text()[contains(.,'{value}')]]")
        input_id = radio_label.get_attribute("for")
        radio_btn = el.find_element(by="xpath",value=f".//input[contains(@id,'{input_id}')]")
        radio_btn.click()
        sleep(0.5)
        radio_btn.click()

    # Example: Field with label 'Province of Territory with data-automation-id=addressSection_countryRegion
    def _select_dropdown(self,el:WebElement, value:str):
        button = el.find_element(by="xpath",value=f".//button")
        button.send_keys(Keys.ENTER)
        sleep(0.5)
        button.click()
        ll = el.find_element("xpath","//div[starts-with(@class,'wd-popup')]")
        ll.find_element("xpath",f".//*[text()[contains(.,'{value}')]]").click()

    def _fill_simple_text_input(self,el:WebElement,value:str):
        el.find_element("xpath",".//input").send_keys(value)


    def _get_progress(self):
        progress_bar = self.driver.find_element("xpath","//div[contains(@data-automation-id,'progressBar')]")
        levels = progress_bar.find_elements("xpath",".//div[@data-automation-id]")
        res:Dict[str,Any] = {"completed":None,"not_completed":None}
        for level in levels:
            label = level.find_element("xpath", ".//label[not(@aria-live)]").text
            did = level.get_attribute('data-automation-id').lower() #type: ignore
            match did:
                case did if did and did.find("completed") != -1:
                    if res["completed"] is None:
                        res["completed"] = [label]
                    else:
                        res["completed"].append(label)
                case did if did and did.find("inactive") != -1:
                    if res["not_completed"] is None:
                        res["not_completed"] = [label]
                    else:
                        res["not_completed"].append(label)
                case did if did and did.find("active") != -1:
                    res["current"] = label
                case _:
                    raise
        return res


    def _fill_my_experience(self,website='myworkday',selected_sections:list|None=None):

        sections = self.definitions["key_map"][website]

        for section_name, sequence in sections.items():
            # If we set specific section to fill, we can use them
            # (Only for development)
            if selected_sections and section_name not in selected_sections:
                continue
            # Make sure to reset current_element for each section
            self.current_element = self.driver.find_element('xpath',"//body")
            data = self.definitions[section_name]["data"]
            # Run the sequence for meta (primer)
            self._run_sequence(sequence["meta"],0.5)

            # Run the sequence for repeated data
            if type(data) == list:
                for d in data:
                    self._run_sequence(sequence["actions"],0.5,d)
                    sleep(2)
            elif type(data) == dict:
                self._run_sequence(sequence["actions"],0.5,data)
            else:
                raise Exception("Wrong type for data. Must be dict or list")

    def _run_sequence(self, actions:List[str],pause:float|None=None,data:dict|None=None):
        if actions[0] == "USE_MANUAL":
            actions.pop(0)
            self._make_manual(actions,pause,data)
        else:
            chain_obj = ActionChains(self.driver)
            self._make_chain(chain_obj,actions,pause,data)
            chain_obj.perform()
            chain_obj.reset_actions()


    def _make_manual(self,actions:List[str],pause:float|None=None,data:dict|None=None):
        assert self.current_element is not None
        for action in actions:
            match action:
                case "CLICK":
                    self.current_element.click()
                case "TAB":
                    self.current_element.send_keys(Keys.TAB)
                case "ENTER":
                    self.current_element.send_keys(Keys.ENTER)
                case "SPACE":
                    self.current_element.send_keys(Keys.SPACE)
                case action if action.find("?")!=-1:
                    command, what = action.split("?")
                    match command:
                        case "WAIT":
                            sleep(float(what))
                        case "SEND":
                            self.current_element.send_keys(what)
                        case "ELEMENT":
                                self.current_element = self.current_element.find_element('xpath',what)
                        case _:
                            raise Exception("Unexpected command name in run manual")
                case _:
                    assert data
                    if type(data[action]) == str:
                        self.current_element.send_keys(data[action])
                    elif type(data[action]) == list:
                        self.current_element.send_keys("\n".join(data[action]))
            if pause:
                sleep(pause)


    def _make_chain(self,chain_obj:ActionChains,actions:List[str],pause:float|None=None,data:dict|None=None):
        assert self.current_element is not None
        for action in actions:
            match action:
                case "CLICK":
                    chain_obj.click()
                case "CLICK_EL":
                    chain_obj.click(self.current_element)
                case "TAB":
                    chain_obj.send_keys(Keys.TAB)
                case "ENTER":
                    chain_obj.send_keys(Keys.ENTER)
                case "SPACE":
                    chain_obj.send_keys(Keys.SPACE)
                case "MOVE":
                    chain_obj.move_to_element(self.current_element)
                case "SCROLL":
                    chain_obj.scroll_to_element(self.current_element)
                case action if action.find("?")!=-1:
                    command, what = action.split("?")
                    match command:
                        case "WAIT":
                            chain_obj.pause(float(what))
                        case "SEND":
                            chain_obj.send_keys(what)
                        case "ELEMENT":
                                self.current_element = self.current_element.find_element('xpath',what)
                        case "SCROLL":
                            chain_obj.scroll_by_amount(delta_x=0,delta_y=int(what))
                        case _:
                            raise Exception("Unexpected command name in chain")
                case _:
                    # For description, since it is multiline we have a list of lines:
                    assert data
                    if type(data[action]) == str:
                        chain_obj.send_keys(data[action])
                    elif type(data[action]) == list:
                        chain_obj.send_keys("\n".join(data[action]))
            if pause:
                chain_obj.pause(pause)