import unittest
from selenium import webdriver
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.keys import Keys

MANAGER_ROOT_URL = 'http://34.229.238.197/'

MANAGER_PAGE_URLS = [
        MANAGER_ROOT_URL + "students",
        MANAGER_ROOT_URL + "tests"
    ]

LOGINS = {
    "manager": "dev@tarex.me",
    "professor": "dev3@tarex.me"
}

class TestFrontend(unittest.TestCase):
    def test_managers(self):
        web_driver = webdriver.Firefox()
        web_driver.implicitly_wait(10)

        web_driver.get(MANAGER_ROOT_URL)

        login(LOGINS['manager'], self, web_driver)

        navigation_links = web_driver.find_elements_by_class_name('nav-link')
        urls = map(lambda l: l.get_attribute('href'), navigation_links)

        for url in MANAGER_PAGE_URLS:
            self.assertIn(url, urls)
            web_driver.get(url)
            self.assertEqual(url, web_driver.current_url)
            test_page_actions(url, self, web_driver)

        logout(self, web_driver)

        web_driver.close()


def login(email: str, test_case: TestFrontend, web_driver: WebDriver):
    web_driver.get(MANAGER_ROOT_URL + "login")
    login_input = web_driver.find_element_by_id("email")
    login_input.send_keys(email)
    password_input = web_driver.find_element_by_id('password')
    password_input.send_keys(email)
    login_button = web_driver.find_element_by_class_name('btn-primary')
    login_button.click()
    test_case.assertEqual(web_driver.current_url, MANAGER_ROOT_URL + 'home')
    message_box = web_driver.find_element_by_class_name('card-body')
    test_case.assertIn('You are logged in!', message_box.text)
    login_name = web_driver.find_element_by_id('navbarDropdown')
    test_case.assertIn(email, login_name.text)

def logout(test_case: TestFrontend, web_driver: WebDriver):
    nav_bar = web_driver.find_element_by_id('navbarDropdown')
    nav_bar.click()
    logout_button = web_driver.find_element_by_class_name('dropdown-item')
    logout_button.click()
    test_case.assertIn(web_driver.current_url, MANAGER_ROOT_URL)


def test_page_actions(page_url: str, test_case: TestFrontend, web_driver: WebDriver):
    if page_url == MANAGER_PAGE_URLS[0]:
        view_button = web_driver.find_element_by_class_name('btn-success')
        preview_fields = \
            filter(lambda e: e != 'View',
                   map(lambda e: e.text, web_driver.find_elements_by_tag_name('td')))
        view_button.click()
        student_fields = map(lambda e: e.text, web_driver.find_elements_by_tag_name('td'))
        for field in preview_fields:
            test_case.assertIn(field, student_fields)
    elif page_url == MANAGER_PAGE_URLS[1]:
        # TODO
        pass

    elif page_url == MANAGER_PAGE_URLS[2]:
        # TODO
        pass

if __name__ == "__main__":
    unittest.main()
