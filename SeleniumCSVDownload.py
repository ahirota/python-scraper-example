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

class SeleniumCSV:

    # Class Constant: Login Page
    login_path = 'LOGIN URL PATH HERE'

    # Class Constant: Pathway for Normal CSV with GET Request
    get_path = 'NORMAL CSV URL PATH HERE'

    # Class Constant: Pathway for Zipped CSV with GET Request
    zip_path = 'ZIP CSV URL PATH HERE'

    # Class Constant: Pathway for Normal CSV with POST Request
    post_path = 'POST CSV URL PATH HERE'

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
        schema = Schema({'csv_type': str,
                         'username': str,
                         'password': str})
        schema.validate(input)
        return self

    # Method for calling and retrieving data from CSV Endpoints
    def get_report_data(self):
        try:
            if self.csv_type == 'zip':
                self.__login_and_verify_credentials()
                data = self.__get_csv_get_zip_data()
            elif self.csv_type == 'post':
                self.__login_and_verify_credentials()
                data = self.__get_csv_post_data()
            else:
                self.__login_and_verify_credentials()
                data = self.__get_csv_get_data()
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

    # Helper Method for getting csv data from GET request
    def __get_csv_get_data(self):
        # Set URL to where you click for Download location
        url = self.get_path
        cookies = self.driver.get_cookies()
        s = requests.Session()
        for cookie in cookies:
            s.cookies.set(cookie['name'], cookie['value'])
        csv = s.get(url)
        # String IO for CSV
        df = pd.read_csv(StringIO(csv.text))
        return df.to_json(orient='values')

    # Helper Method for getting zipped csv data from GET request
    def __get_csv_get_zip_data(self):
        # Set URL to where you click for Download location
        url = self.zip_path
        cookies = self.driver.get_cookies()
        s = requests.Session()
        for cookie in cookies:
            s.cookies.set(cookie['name'], cookie['value'])
        csv = s.get(url)
        # Bytes IO with ZipFile to unwrap data for CSV
        df = pd.read_csv((ZipFile(BytesIO(csv.content)).open('report.csv')))
        return df.to_json(orient='values')

    # Helper Method for getting csv data from POST request
    def __get_csv_post_data(self):
        # Set URL to where you click for Download location
        url = self.post_path
        data = dict(paramStr='CSV_PARAMETERS')
        cookies = self.driver.get_cookies()
        s = requests.Session()
        for cookie in cookies:
            s.cookies.set(cookie['name'], cookie['value'])
        csv = s.post(url, data=data)
        df = pd.read_csv(StringIO(csv.text))
        return df.to_json(orient='values')

# Main Method
def main(args):
    csv = SeleniumCSV(args)
    data = csv.get_report_data()
    del csv
    return data


if __name__ == '__main__':
    print(main(sys.argv[1]))
