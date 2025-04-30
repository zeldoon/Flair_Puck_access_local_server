from playwright.sync_api import Page
import re

class Locators:

    def __init__(self, page: Page):
        ## TEXT CONSTANTS
        HOW_CAN_WE_HELP = 'How can we help?'


        self.page = page

        self.navicon = page.get_by_test_id('nav-icon')
        self.sign_in_button = page.get_by_role('button').get_by_text("Sign In")

        ## UNFINISHED HOMES
        self.unfinished_setup_dialog = page.get_by_test_id('unfinished-setup-dialog')
        self.unfinished_setup_close = page.get_by_test_id('unfinished-setup-close')
        self.homes_menu_title = page.get_by_test_id('homes-menu-title')
        self.homes_menu = page.locator('#home-selection-menu')
        self.incomplete_structure = page.get_by_test_id(re.compile(r'incomplete-structure\d+'))

        ## FLAIR MENU LAYOUT
        self.flair_menu_home_settings = page.get_by_test_id('navbar-home-settings')
        self.flair_menu_home_statistics = page.get_by_test_id('navbar-home-statistics')
        self.flair_menu_admin_mode = page.get_by_test_id('navbar-admin-mode')
        self.flair_menu_home_logs = page.get_by_test_id('navbar-home-logs')
        self.flair_menu_home_manual = page.get_by_test_id('navbar-home-manual')
        self.flair_menu_occupancy_explanations = page.get_by_test_id('navbar-occupancy-explanations')
        self.flair_menu_get_support = page.get_by_test_id('navbar-get-support')
        self.flair_menu_notifications = page.get_by_test_id('navbar-notifications')
        self.flair_menu_account_settings = page.get_by_test_id('navbar-account-settings')
        self.flair_menu_sign_out = page.get_by_test_id('navbar-sign-out')
        self.flair_menu_sign_in = page.get_by_test_id('navbar-sign-in')
        self.support_modal_title = page.locator('.MuiDialogTitle-root > h2', has_text=HOW_CAN_WE_HELP)

        ## STRUCTURE VIEW CONTROL BAR
        self.control_home_away = page.get_by_test_id('status-home-away')
        self.control_weather = page.get_by_test_id('status-weather')
        self.control_set_point = page.get_by_test_id('status-set-point')
        self.control_system_mode = page.get_by_test_id('testid-vent-mode')
        self.control_heat_cool_mode = page.get_by_test_id('testid-heato-mode') #sic
        self.control_schedule = page.get_by_test_id('status-schedule')
