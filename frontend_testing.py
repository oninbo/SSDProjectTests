import unittest
import time
from typing import List
from selenium import webdriver
from selenium.webdriver.firefox.webdriver import WebDriver
import psutil

GECKO_DRIVER = 'geckodriver'

MP_ROOT_URL = 'http://34.229.238.197/'

MANAGER_PAGE_URLS = [
        MP_ROOT_URL + "students",
        MP_ROOT_URL + "tests"
    ]

PROFESSOR_PAGE_URLS = [
        MP_ROOT_URL + "schedules"
    ]

LOGINS = {
    "manager": "dev@tarex.me",
    "professor": "dev3@tarex.me"
}

class TestFrontend(unittest.TestCase):
    def test_managers(self):
        web_driver = create_web_driver()
        web_driver.get(MP_ROOT_URL)

        login(LOGINS['manager'], self, web_driver)

        navigation_links = web_driver.find_elements_by_class_name('nav-link')
        urls = set(map(lambda l: l.get_attribute('href'), navigation_links))

        for url in MANAGER_PAGE_URLS:
            self.assertIn(url, urls)
            web_driver.get(url)
            self.assertEqual(url, web_driver.current_url)
            _test_page_actions(url, self, web_driver)

        logout(self, web_driver)

        web_driver_quit(web_driver, self)

def create_web_driver() -> WebDriver:
    web_driver = webdriver.Firefox()
    web_driver.implicitly_wait(10)
    return web_driver

def web_driver_quit(web_driver: WebDriver, test_case: TestFrontend):
    web_driver.quit()
    test_case.assertFalse(GECKO_DRIVER in (p.name() for p in psutil.process_iter()))


def login(email: str, test_case: TestFrontend, web_driver: WebDriver):
    web_driver.get(MP_ROOT_URL + "login")
    login_input = web_driver.find_element_by_id("email")
    login_input.send_keys(email)
    password_input = web_driver.find_element_by_id('password')
    password_input.send_keys(email)
    login_button = web_driver.find_element_by_class_name('btn-primary')
    login_button.click()
    test_case.assertEqual(web_driver.current_url, MP_ROOT_URL + 'home')
    message_box = web_driver.find_element_by_class_name('card-body')
    test_case.assertIn('You are logged in!', message_box.text)
    login_name = web_driver.find_element_by_id('navbarDropdown')
    test_case.assertIn(email, login_name.text)

def logout(test_case: TestFrontend, web_driver: WebDriver):
    nav_bar = web_driver.find_element_by_id('navbarDropdown')
    nav_bar.click()
    logout_button = web_driver.find_element_by_class_name('dropdown-item')
    logout_button.click()
    test_case.assertIn(web_driver.current_url, MP_ROOT_URL)

def _create_delete_test(test_name: str, web_driver: WebDriver, test_case: TestFrontend):
    create_test_link = \
        web_driver.find_element_by_class_name('card-header').find_element_by_tag_name('a')
    create_test_link.click()
    test_case.assertEqual(web_driver.current_url, MANAGER_PAGE_URLS[1] + '/create')
    name_input = web_driver.find_element_by_id('name')
    name_input.send_keys(test_name)
    create_button = web_driver.find_element_by_class_name('btn-success')
    create_button.click()
    table_values = _get_table_values(web_driver)
    test_case.assertIn(test_name, table_values)
    last_delete_button = web_driver.find_elements_by_class_name('btn-danger')[-1]
    last_delete_button.click()
    test_case.assertNotIn(test_name, _get_table_values(web_driver))

def _edit_test(web_driver: WebDriver, test_case: TestFrontend):
    def get_edit_button():
        return web_driver.find_element_by_class_name('btn-primary')

    def get_name_input():
        return web_driver.find_element_by_id('name')

    def get_update_btn():
        return web_driver.find_element_by_class_name('btn-success')
    edit_button = get_edit_button()
    old_name = web_driver.find_element_by_tag_name('td').text
    edit_button.click()
    test_case.assertIn('edit', web_driver.current_url)
    name_input = get_name_input()
    name_input.clear()
    new_name = f'{old_name} #{int(time.time())}'
    name_input.send_keys(new_name)
    update_button = get_update_btn()
    update_button.click()
    _check_table_fields([new_name], web_driver, test_case)
    edit_button = get_edit_button()
    edit_button.click()
    name_input = get_name_input()
    name_input.clear()
    name_input.send_keys(old_name)
    update_button = get_update_btn()
    update_button.click()
    _check_table_fields([new_name], web_driver, test_case)
    _check_table_fields([old_name], web_driver, test_case)

def _get_table_values(web_driver: WebDriver):
    return set(map(lambda e: e.text, web_driver.find_elements_by_tag_name('td')))

def _check_table_fields(preview_fields: List[str], web_driver: WebDriver, test_case: TestFrontend):
    check_fields = _get_table_values(web_driver)
    for field in preview_fields:
        test_case.assertIn(field, check_fields)

def _get_int_time() -> int:
    return int(time.time())

def _create_delete_answer(web_driver: WebDriver, test_case: TestFrontend):
    view_button = web_driver.find_element_by_class_name('btn-success')
    view_button.click()
    create_link = web_driver.find_element_by_class_name('card-header').find_element_by_tag_name('a')
    create_link.click()
    question_input = web_driver.find_elements_by_id('question')
    question_name = f'My Cool Question #{_get_int_time()}'
    question_input.send_keys(question_name)
    create_button = web_driver.find_element_by_class_name('btn-success')
    create_button.click()
    _check_table_fields([question_name], web_driver, test_case)
    delete_button = web_driver.find_elements_by_class_name('btn-danger')[-1]
    delete_button.click()
    _check_table_fields([question_name], web_driver, test_case)

def _test_page_actions(page_url: str, test_case: TestFrontend, web_driver: WebDriver):
    if page_url == MANAGER_PAGE_URLS[0]:
        view_button = web_driver.find_element_by_class_name('btn-success')
        preview_fields = \
            set(filter(lambda f: f != 'View',
                       map(lambda e: e.text, web_driver.find_elements_by_tag_name('td'))))
        view_button.click()
        test_case.assertGreater(len(preview_fields & _get_table_values(web_driver)), 0)

if __name__ == "__main__":
    unittest.main()
