from typing import Any, Dict, List
from urllib.parse import urlparse
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver import Keys, ActionChains

from airflow.decorators import task

from time import sleep
import json
import re

driver = driver
current_element: WebElement|None = None
url = url
creds_db = creds_db

my_information_fields = {
    "formField-sourcePrompt": lambda el: _fill_multi_select_container(el,"formField-sourcePrompt","a"),
    "formField-":lambda el: _select_radio_button(el,"No"),
    "formField-countryDropdown":None,
    "formField-legalNameSection_firstName":lambda el: _fill_simple_text_input(el,"Ahamad"),
    "formField-legalNameSection_lastName":lambda el: _fill_simple_text_input(el,"Noori"),
    "formField-formField-preferredNameCheckbox":None,
    "formField-addressSection_addressLine1":lambda el: _fill_simple_text_input(el,"Your Mama's Home"),
    "formField-addressSection_city":lambda el: _fill_simple_text_input(el,"Toronto"),
    "formField-addressSection_countryRegion":lambda el: _select_dropdown(el,"Ontario"),
    "formField-addressSection_postalCode":lambda el: _fill_simple_text_input(el,"M2M 1E1"),
    "formField-email":None,
    "formField-phone-device-type":None,
    "formField-country-phone-code":None,
    "formField-phone-number":lambda el: _fill_simple_text_input(el,"4166969699"),
    "formField-phone-extension":None
}
definitions = json.load(open(def_address))


#TODO: Add this to params later  
# def get_base_url(url):
#     parsed_url = urlparse(url)
#     return f"{parsed_url.scheme}://{parsed_url.netloc}"
# base_url = get_base_url(url)

@task
def get_creds(params:dict|None=None):
    assert params and "base_url" in params
    base_url = params["base_url"]
    with open(creds_db,"r") as f:
        f.readline()
        for line in f:
            fields = line.rstrip().split(",")
            if fields[0].find(base_url) != -1:
                usr, passwd = fields[1:]
                return usr, passwd 
    raise Exception(f"Could not find user and password for base url: {base_url}")

# ****** Actions *******

@task
def goto_url(params:dict):
    driver.get(params["url"])


@task
def pause(duration:float=1):
    sleep(duration)

@task
def refresh():
    driver.refresh()

def sign_in():
    usr, passwd = get_creds()
    _perform_sign_in(usr,passwd)
    return 

def my_information():
    _fill_my_information()
    return 

def find_click_submit_btn():
    _find_submit_or_next_btn().click()
    return 

def my_experience(selected_sections:list|None=None):
    _fill_my_experience(selected_sections=selected_sections)
    return 

# ****** End of Actions *******
    
# def run( url:str):
    # current_page = get_progress()['current']
    # match current_page:
    #     case "My Information":
    #         my_information()
    #     case "My Experience":
    #         my_experience()    

# *** Fill Pages ***
def _perform_sign_in(user:str, password:str):
    sign_in_form = driver.find_element("xpath","//form[contains(@data-automation-id,'signInFormo')]")
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
    ActionChains(driver).move_to_element(btn).pause(0.5).send_keys(Keys.ENTER).pause(0.5).click().perform()

def _fill_my_information():
    #TODO: This must be integrated with the definitions json framework later 
    f_list = driver.find_elements("xpath","//div[contains(@data-automation-id,'formField')]")
    print(f_list)
    for f in f_list:
        func = my_information_fields.get(f.get_attribute('data-automation-id')) # type: ignore
        if func is not None:
            try:
                func(f)
            except Exception as e:
                print(f"Error for {f.get_attribute('data-automation-id')}")
                print(e)
            sleep(1)

def _find_submit_or_next_btn():
    pattern = re.compile(r".*save|next|done|submit.*",re.IGNORECASE)
    btns = driver.find_elements("xpath","//button")
    for btn in btns:
        if pattern.match(btn.text):
            return btn
    raise Exception("Submit button not found")


# *** End Fill Pages ***

def _fill_multi_select_container(el:WebElement,data_automation_id:str, value:str):
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


def _select_radio_button(el:WebElement, value:str):
    radio_label = el.find_element(by="xpath",value=f".//label[text()[contains(.,'{value}')]]")
    input_id = radio_label.get_attribute("for")
    radio_btn = el.find_element(by="xpath",value=f".//input[contains(@id,'{input_id}')]")
    radio_btn.click()
    sleep(0.5)
    radio_btn.click()

# Example: Field with label 'Province of Territory with data-automation-id=addressSection_countryRegion
def _select_dropdown(el:WebElement, value:str):
    button = el.find_element(by="xpath",value=f".//button")
    button.send_keys(Keys.ENTER)
    sleep(0.5)
    button.click()
    ll = el.find_element("xpath","//div[starts-with(@class,'wd-popup')]")
    ll.find_element("xpath",f".//*[text()[contains(.,'{value}')]]").click()

def _fill_simple_text_input(el:WebElement,value:str):
    el.find_element("xpath",".//input").send_keys(value)


def _get_progress():
    progress_bar = driver.find_element("xpath","//div[contains(@data-automation-id,'progressBar')]")
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


def _fill_my_experience(website='myworkday',selected_sections:list|None=None):

    sections = definitions["key_map"][website]

    for section_name, sequence in sections.items():
        # If we set specific section to fill, we can use them
        # (Only for development)
        if selected_sections and section_name not in selected_sections:
            continue
        # Make sure to reset current_element for each section
        current_element = driver.find_element('xpath',"//body")
        data = definitions[section_name]["data"]
        # Run the sequence for meta (primer)
        _run_sequence(sequence["meta"],0.5)

        # Run the sequence for repeated data
        if type(data) == list:
            for d in data:
                _run_sequence(sequence["actions"],0.5,d)
                sleep(2)
        elif type(data) == dict:
            _run_sequence(sequence["actions"],0.5,data)
        else:
            raise Exception("Wrong type for data. Must be dict or list")

def _run_sequence( actions:List[str],pause:float|None=None,data:dict|None=None):
    if actions[0] == "USE_MANUAL":
        actions.pop(0)
        _make_manual(actions,pause,data)
    else:
        chain_obj = ActionChains(driver)
        _make_chain(chain_obj,actions,pause,data)
        chain_obj.perform()
        chain_obj.reset_actions()


def _make_manual(actions:List[str],pause:float|None=None,data:dict|None=None):
    assert current_element is not None
    for action in actions:
        match action:
            case "CLICK":
                current_element.click()
            case "TAB":
                current_element.send_keys(Keys.TAB)
            case "ENTER":
                current_element.send_keys(Keys.ENTER)
            case "SPACE":
                current_element.send_keys(Keys.SPACE)
            case action if action.find("?")!=-1:
                command, what = action.split("?")
                match command:
                    case "WAIT":
                        sleep(float(what))
                    case "SEND":
                        current_element.send_keys(what)
                    case "ELEMENT":
                            current_element = current_element.find_element('xpath',what)
                    case _:
                        raise Exception("Unexpected command name in run manual")
            case _:
                assert data
                if type(data[action]) == str:
                    current_element.send_keys(data[action])
                elif type(data[action]) == list:
                    current_element.send_keys("\n".join(data[action]))
        if pause:
            sleep(pause)


def _make_chain(chain_obj:ActionChains,actions:List[str],pause:float|None=None,data:dict|None=None):
    assert current_element is not None
    for action in actions:
        match action:
            case "CLICK":
                chain_obj.click()
            case "CLICK_EL":
                chain_obj.click(current_element)
            case "TAB":
                chain_obj.send_keys(Keys.TAB)
            case "ENTER":
                chain_obj.send_keys(Keys.ENTER)
            case "SPACE":
                chain_obj.send_keys(Keys.SPACE)
            case "MOVE":
                chain_obj.move_to_element(current_element)
            case "SCROLL":
                chain_obj.scroll_to_element(current_element)
            case action if action.find("?")!=-1:
                command, what = action.split("?")
                match command:
                    case "WAIT":
                        chain_obj.pause(float(what))
                    case "SEND":
                        chain_obj.send_keys(what)
                    case "ELEMENT":
                            current_element = current_element.find_element('xpath',what)
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