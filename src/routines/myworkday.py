"""
So far this is only tested for TD: https://td.wd3.myworkdayjobs.com/
"""
import json
from typing import Any, Dict, List
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver import Keys, ActionChains
from time import sleep

my_information_fields = {
    "formField-sourcePrompt": lambda el: fill_multi_select_container(el,"formField-sourcePrompt","a"),
    "formField-":lambda el: select_radio_button(el,"No"),
    "formField-countryDropdown":None,
    "formField-legalNameSection_firstName":lambda el: fill_simple_text_input(el,"Ahamad"),
    "formField-legalNameSection_lastName":lambda el: fill_simple_text_input(el,"Noori"),
    "formField-formField-preferredNameCheckbox":None,
    "formField-addressSection_addressLine1":lambda el: fill_simple_text_input(el,"Your Mama's Home"),
    "formField-addressSection_city":lambda el: fill_simple_text_input(el,"Toronto"),
    "formField-addressSection_countryRegion":lambda el: select_dropdown(el,"Ontario"),
    "formField-addressSection_postalCode":lambda el: fill_simple_text_input(el,"M2M 1E1"),
    "formField-email":None,
    "formField-phone-device-type":None,
    "formField-country-phone-code":None,
    "formField-phone-number":lambda el: fill_simple_text_input(el,"4166969699"),
    "formField-phone-extension":None
    }


def get_creds(base_url:str):
    with open("db/creds.csv","r") as f:
        f.readline()
        for line in f:
            fields = line.rstrip().split(",")
            if fields[0].find(base_url) != -1:
                return fields[1:]
    return None, None

def run(driver: WebDriver, base_url:str):
    usr, passwd = get_creds(base_url)
    assert usr and passwd
    sleep(2)
    sign_in(driver,usr,passwd)
    sleep(2)
    current_page = get_progress(driver)['current']
    match current_page:
        case "My Information":
            my_information(driver)
        case "My Experience":
            ...

# *** Fill Pages ***
def sign_in(driver: WebDriver, user:str, password:str):
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

def my_information(driver: WebDriver):
    f_list = driver.find_elements("xpath","//div[contains(@data-automation-id,'formField')]")
    for f in f_list:
        func = my_information_fields.get(f.get_attribute('data-automation-id')) # type: ignore
        if func is not None:
            try:
                func(f)
            except Exception as e:
                print(f"Error for {f.get_attribute('data-automation-id')}")
                print(e)
            sleep(1)

def my_experience(driver: WebDriver):
    section_name_map = {
        "workExperienceSection": "work_experience",
        "educationSection": "education",
        # "languageSection": "language",
        # "skillsSection": "skills",
        # "resumeSection": "resume",
        # "websiteSection": "website",
        # "socialNetworkSection": "social_network"
    }

    sections = driver.find_elements("xpath","//div[contains(@data-automation-id,'Section') and not(@class)]")
    definitions = json.load(open("src/routines/experience_definitions.json"))
    chain = ActionChains(driver)
    
    def perform_filling(chain:ActionChains, section:WebElement, section_name:str):
        data = definitions[section_name]["data"]
        sequence = definitions["key_map"]["myworkday"][section_name]
        add_btn = section.find_element("xpath",".//button[contains(@data-automation-id,'Add')]")
        for d in data:
            make_chain(chain,add_btn,d,sequence)
            chain.perform()
            sleep(2)
            add_btn = driver.switch_to.active_element

    for section in sections:
        section_attr = section.get_attribute('data-automation-id')
        assert section_attr
        section_name = section_name_map.get(section_attr)
        if section_name is None:
            continue
        perform_filling(chain,section,section_name)
        sleep(2)



# *** End Fill Pages ***

def fill_multi_select_container(el:WebElement,data_automation_id:str, value:str):
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

# def get_labels(el:WebElement):
#     labels = el.find_elements(by="xpath",value=f".//label")
#     return [l.text for l in labels]


def select_radio_button(el:WebElement, value:str):
    radio_label = el.find_element(by="xpath",value=f".//label[text()[contains(.,'{value}')]]")
    input_id = radio_label.get_attribute("for")
    radio_btn = el.find_element(by="xpath",value=f".//input[contains(@id,'{input_id}')]")
    radio_btn.click()
    sleep(0.5)
    radio_btn.click()

# Example: Field with label 'Province of Territory with data-automation-id=addressSection_countryRegion
def select_dropdown(el:WebElement, value:str):
    button = el.find_element(by="xpath",value=f".//button")
    button.send_keys(Keys.ENTER)
    sleep(0.5)
    button.click()
    ll = el.find_element("xpath","//div[starts-with(@class,'wd-popup')]")
    ll.find_element("xpath",f".//*[text()[contains(.,'{value}')]]").click()

def fill_simple_text_input(el:WebElement,value:str):
    el.find_element("xpath",".//input").send_keys(value)


def get_progress(driver:WebDriver):
    progress_bar = driver.find_element("xpath","//div[contains(@data-automation-id,'progressBar')]")
    levels = progress_bar.find_elements("xpath",".//div[@data-automation-id]")
    res:Dict[str,Any] = {"completed":None,"not_completed":None}
    for level in levels:
        label = level.find_element("xpath", ".//label[not(@aria-live)]").text
        did = level.get_attribute('data-automation-id').lower()
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

def populate_exp_sections(el:WebDriver, section_id:str, info:list):
    add_btn = el.find_element("xpath",".//button[contains(@data-automation-id,'Add')]")
    add_btn.click()

def make_chain(chain:ActionChains, el:WebElement, data:dict, sequence:List[str]):
    chain.move_to_element(el)
    def key_actions(action:str):
        match action:
            case "CLICK":
                chain.click()
            case "TAB":
                chain.send_keys(Keys.TAB)
            case "ENTER":
                chain.send_keys(Keys.ENTER)
            case "SPACE":
                chain.send_keys(Keys.SPACE)
            case action if action.find("?")!=-1:
                command, what = action.split("?")
                match command:
                    case "WAIT":
                        chain.pause(float(what))
                    case "SEND":
                        chain.send_keys(what)
                    case _:
                        raise Exception("Undefined command name in chan")
            case _:
                # For description, since it is multiline we have a list of lines:
                if type(data[action]) == str:
                    chain.send_keys(data[action])
                elif type(data[action]) == list:
                    chain.send_keys("\n".join(data[action]))

            
    for action in sequence:
        key_actions(action)