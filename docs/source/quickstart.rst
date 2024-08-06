============
Quick Start
============ 

Fill a simple Workday from
==========================

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


Use bidi Module to implement a page mutation observer
=====================================================

First, activate the debug mode in google chrome in bash:

.. code-block:: console

    google-chrome --remote-debugging-port=9222 --remote-allow-origins=*

Then:

.. code-block:: python

    from dotenv import load_dotenv
    from src.driver import Driver
    from src.bidi import Bidi

    load_dotenv()
    # Attach the webdriver to an already open google chrome session (debugger must be activated)
    driver = Driver(load_timeout=-1, driver_logging=False,debug_address="localhost:9222")

    bidi = Bidi(driver.driver)

    # Inject a mutation observer script
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
    """ %(bidi.output_node_id)
    observer_uid = bidi.inject_script(script)

    # Start The mutation observer script
    target = "body"
    script = """
        const targetNode = document.getElementsByTagName('%s');
        const config = { attributes: true, childList: true, subtree: true };
        // Start observing the target node for configured mutations
        observer.observe(targetNode[0], config);
    """ % (target)
    starter_uid = bidi.inject_script(script)

    # Do some action on the page that leads to change ....
    # Then to get the diff mutations, run:

    output = bidi.get_raw_output()

    # Do some extra work with it...
    # Once you're done with the observer, remove it:
    uid = bidi.inject_script("observer.disconnect()")
    bidi.destroy_node(uid,observer_uid,starter_uid)