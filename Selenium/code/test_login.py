import os
import time
from collections import namedtuple

import pytest
from _pytest.fixtures import FixtureRequest
from selenium.webdriver import ActionChains

from ui.pages.base_page import BasePage
from ui.locators import basic_locators

from selenium.webdriver.common.keys import Keys


class BaseCase:
    authorize = True

    @pytest.fixture(scope='function', autouse=True)
    def setup(self, driver, config, request: FixtureRequest):
        self.driver = driver
        self.config = config

        self.login_page = LoginPage(driver)
        if self.authorize:
            credentials = request.getfixturevalue('credentials')
            self.login_page.click(self.login_page.locators.LOGIN_BUTTON)

            login_input = self.login_page.find(self.login_page.locators.LOGIN_INPUT)
            password_input = self.login_page.find(self.login_page.locators.PASSWORD_INPUT)

            login_input.clear()
            password_input.clear()

            login_input.send_keys(credentials['login'])
            password_input.send_keys(credentials['password'])
            password_input.send_keys(Keys.ENTER)

            self.main_page = self.login_page.login()
            # self.profile_settings_page =


@pytest.fixture(scope='session')
def credentials():
    login = os.getenv('VK_QA_SEM_LOGIN')
    password = os.getenv('VK_QA_SEM_PASSWORD')
    creds = {
        'login': login,
        'password': password
    }
    return creds


@pytest.fixture(scope='session')
def cookies(credentials, config):
    pass


class BaseParkPage(BasePage):
    locators = basic_locators.BaseParkPageLocators()


class LoginPage(BaseParkPage):
    url = 'https://park.vk.company/'

    def login(self):
        return MainPage(self.driver)


class MainPage(BaseParkPage):
    locators = basic_locators.MainPageParkLocators()
    url = 'https://park.vk.company/feed/'


# class SettingsPage(BaseParkPage):
#     def is_opened(self, timeout=15):
#         return True



class TestLogin(BaseCase):
    authorize = True
    LOGIN_REDIRECT_URL = 'https://park.vk.company/feed/'

    def test_login(self):
        assert self.driver.current_url == self.LOGIN_REDIRECT_URL
        logo = self.login_page.find(self.login_page.locators.LOGO_IMG)
        logo_title = logo.get_attribute('title')
        assert logo_title == 'Образовательный центр VK в МГТУ'


PageRedirectData = namedtuple('PageRedirectData', ['button_locator', 'element_locator', 'element_text'])


class TestRedirect(BaseCase):
    authorize = True

    @pytest.mark.parametrize(
        'pages',
        [
            [
                PageRedirectData(basic_locators.MainPageParkLocators.BLOGS_BUTTON,
                                 basic_locators.MainPageParkLocators.BLOGS_CONTENT_TITLE,
                                 'Все блоги'),
                PageRedirectData(basic_locators.MainPageParkLocators.PEOPLE_BUTTON,
                                 basic_locators.MainPageParkLocators.PEOPLE_CONTENT_TITLE,
                                 'Сообщество проекта'),
            ],
            [
                PageRedirectData(basic_locators.MainPageParkLocators.PROGRAM_BUTTON,
                                 basic_locators.MainPageParkLocators.MAIN_PROGRAMS_TITLE,
                                 'Основные программы'),
                PageRedirectData(basic_locators.MainPageParkLocators.ALUMNI_BUTTON,
                                 basic_locators.MainPageParkLocators.ALUMNI_CONTENT_TITLE,
                                 'Наши выпускники'),
            ]
        ]
    )
    def test_redirect(self, pages: list[PageRedirectData]):
        for redirect_button_loc, identifying_element_loc, element_text in pages:
            self.main_page.click(redirect_button_loc)
            element = self.main_page.find(identifying_element_loc)
            assert element.get_attribute('innerText').strip() == element_text


class TestProfileSettings(BaseCase):
    authorize = True

    def test_change_profile_about(self):
        self.main_page.click(self.main_page.locators.USER_DROPDOWN)
        self.main_page.click(self.main_page.locators.USER_MENU_SETTINGS_BUTTON)
        about_textarea = self.main_page.find(self.main_page.locators.PROFILE_ABOUT)
        ActionChains(self.driver).move_to_element(about_textarea).perform()
        about_textarea.send_keys('\nTelegram: @1234\nWeChat: @i_am_not_use_wechat')
        self.main_page.click(self.main_page.locators.SETTINGS_SUBMIT_BUTTON)
        success_msg = self.main_page.find(self.main_page.locators.SETTINGS_SUCCESS_CHANGE_MSG)

        assert success_msg.get_attribute('innerText') == 'Вы успешно отредактировали поле: О себе'



