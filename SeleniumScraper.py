from sysconfig import get_path
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.common.exceptions import NoSuchElementException
from time import sleep
from schema import Schema, And, Use, Optional, SchemaError
from datetime import datetime
from bs4 import BeautifulSoup
import lxml
import requests
import sys
import json
from selenium.webdriver.support.ui import Select
import pandas as pd
import urllib
import os
import certifi
from io import StringIO
from io import BytesIO
from zipfile import ZipFile

class SeleniumScraper:

    # Class Constant: Login Page
    login_path = 'LOGIN URL PATH HERE'

    # Class Constant: Pathway for Paged Data
    paged_path = 'PAGED DATA URL PATH HERE'

    # Class Constant: Pathway for Table Data From Post Request
    table_path = 'TABLE DATA URL PATH HERE'

    # Class Constant: Pathway for Paged Data with Checkbox Form for Viewing Data
    checkbox_path = 'CHECKBOX FORM URL PATH HERE'

    # Constructor Method
    def __init__(self, json_vars):
        try:
            inputs = json.loads(json_vars)

            # Initialize driver first because Destructor Method always ensures that driver will quit
            # Throws an Error if Class Instance is destroyed before Driver is set
            self.driver = webdriver.Remote(command_executor='http://selenium:4444/wd/hub', desired_capabilities=DesiredCapabilities.CHROME.copy())

            # Validate/Verify Input
            self.__validate_input(inputs)

            # Set Instance variables
            self.csv_type = inputs['csv_type']
            self.username = inputs['username']
            self.password = inputs['password']

        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            self.driver.quit()
            print(json.dumps({"err_type": exc_type.__name__,"err_msg": str(exc_value)}))
            exit()

    # Destructor Method
    def __del__(self):
        self.driver.quit()

    # Helper Method for validating input
    def __validate_input(self, input):
        schema = Schema({'data_type': str,
                         'username': str,
                         'password': str})
        schema.validate(input)
        return self

    # Method for calling and retrieving data from CSV Endpoints
    def get_report_data(self):
        try:
            if self.csv_type == 'paged':
                self.__login_and_verify_credentials()
                data = self.__get_data_from_paged_table()
            elif self.csv_type == 'checkbox':
                self.__login_and_verify_credentials()
                data = self.__get_data_from_checkbox_form()
            else:
                self.__login_and_verify_credentials()
                data = self.__get_data_from_table_post_request()
            return data
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            return(json.dumps({"err_type": exc_type.__name__, "err_msg": str(exc_value)}))

    # Helper Method for logging into a site and verifying that you have successfully logged in
    # This is a sample that is designed for a login form with fields that have the IDs 'account' and 'password'
    def __login_and_verify_credentials(self):
        self.driver.get(self.login_path)
        sleep(1)
        self.driver.find_element_by_id('account').send_keys(self.username)
        self.driver.find_element_by_id('password').send_keys(self.password)
        self.driver.find_element_by_xpath('//*[@id="btnSubmit"]').click()
        sleep(1)
        return True

    # Helper Method for getting overview data
    def __get_data_from_checkbox_form(self):
        click = ["Ids","For","Desired","Checked","Parameters"]
        self.driver.get(self.checkbox_path)
        # Open Checkbox Modal
        self.driver.find_element_by_xpath('//*[@id="checkboxOpen"]').click()
        sleep(1)
        form = self.driver.find_element_by_id('checkboxForm')
        elements = form.find_elements_by_name('config_id[]')
        # Uncheck All Elements, Recheck if found in list
        for element in elements:
            if element.get_attribute('checked'):
                element.click()
            if element.get_attribute('value') in click:
                element.click()
        # Submit Checkbox Request
        self.driver.find_element_by_xpath('//*[@id="checkboxSubmit"]').click()
        sleep(1)
        soup = BeautifulSoup(self.driver.page_source, 'lxml')
        # Find Table with Parameters
        table = soup.find('table', {'id':'resultingId'})
        df = pd.read_html(str(table))
        return df[0].to_json(orient='values')

    # Helper Method for getting hourly data
    def __get_data_from_table_post_request(self):
        cookies = self.driver.get_cookies()
        s = requests.Session()
        for cookie in cookies:
            s.cookies.set(cookie['name'], cookie['value'])
        payload = {'Payload for POST request'}
        response = s.post(self.table_path, data=payload)
        soup = BeautifulSoup(response.content, 'lxml')
        table = soup.find('table')
        df = pd.read_html(str(table))
        return df[0].to_json(orient='values')

    # Helper Method for getting item data
    def __get_data_from_paged_table(self):
        loop_flag = True
        pageno = 1
        result_dict = {}
        while loop_flag:
            kwargs = 'HTML_QUERY_HERE' + '&pageno=' + pageno
            self.driver.get(self.paged_path + '?' + kwargs)
            # Returns JSON in text
            data = self.driver.find_element_by_xpath('/html/body/pre').text
            data = json.loads(data)
            # Loop through returned item list and save
            for key, item in data["list"].items():
                result_dict[key] = item
            # Check for next page. if none, break loop
            if data["pager"]["nextLink"]:
                pageno += 1
            else:
                loop_flag = False
        return json.dumps(result_dict)

# Main Method
def main(args):
    scraper = SeleniumScraper(args)
    data = scraper.get_report_data()
    del scraper
    return data


if __name__ == '__main__':
    print(main(sys.argv[1]))
