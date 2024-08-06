Quick Start: Fill a simple Workday from
=======================================

.. code-block:: Python
    
    from dotenv import load_dotenv
    from src.driver import Driver
    from src.scanner import Scanner
    from src.routines.myworkday import Routine
    from selenium.webdriver import Keys, ActionChains
    load_dotenv()
    driver = Driver(load_timeout=-1, driver_logging=False,debug_address="localhost:9222")
    url = "https://link.to.workday.page"
    scanner = Scanner(driver.driver,"div[contains(@data-automation-id,'Page')]")
    routine = Routine(driver.driver,url)
    routine.goto_url().pause(2).sign_in().pause(3).find_click_submit_btn().pause(4).find_click_submit_btn().pause(5).pause(5).my_information().pause(1).find_click_submit_btn().pause(5).my_experience()