class UiConstants:
    def __init__(self):
        """Provide constant values for text, regexes, RBG colors, SVG paths, etc"""

        # RGB COLORS
        self.blue_ring_color = "#1ac6ff"
        self.blue_handle_color = "#16acde"

        # SVG PATHS
        self.cancel_path = "M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"
        self.checkmark_path = "M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"
        self.wrench_path = "M22.7 19l-9.1-9.1c.9-2.3.4-5-1.5-6.9-2-2-5-2.4-7.4-1.3L9 6 6 9 1.6 4.7C.4 7.1.9 10.1 2.9 12.1c1.9 1.9 4.6 2.4 6.9 1.5l9.1 9.1c.4.4 1 .4 1.4 0l2.3-2.3c.5-.4.5-1.1.1-1.4z"
        self.snowflake_path = "M22 11h-4.17l3.24-3.24-1.41-1.42L15 11h-2V9l4.66-4.66-1.42-1.41L13 6.17V2h-2v4.17L7.76 2.93 6.34 4.34 11 9v2H9L4.34 6.34 2.93 7.76 6.17 11H2v2h4.17l-3.24 3.24 1.41 1.42L9 13h2v2l-4.66 4.66 1.42 1.41L11 17.83V22h2v-4.17l3.24 3.24 1.42-1.41L13 15v-2h2l4.66 4.66 1.41-1.42L17.83 13H22z"
        self.left_arrow_path = (
            "M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"
        )
        self.down_arrow_path = (
            "M16.59 8.59L12 13.17 7.41 8.59 6 10l6 6 6-6z"
        )
        self.up_arrow_path = "M12 8l-6 6 1.41 1.41L12 10.83l4.59 4.58L18 14z"
        self.circle_x_path = "M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"
        self.circle_tooltip_path = "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 17h-2v-2h2v2zm2.07-7.75l-.9.92C13.45 12.9 13 13.5 13 15h-2v-.5c0-1.1.45-2.1 1.17-2.83l1.24-1.26c.37-.36.59-.86.59-1.41 0-1.1-.9-2-2-2s-2 .9-2 2H8c0-2.21 1.79-4 4-4s4 1.79 4 4c0 .88-.36 1.68-.93 2.25z"

        # V2A INCOMPLETE STRUCTURE DIALOG
        self.v2a_incomplete_msg = "You have not completed initial setup of <HOME>."
        self.v2a_home_id = "Home ID"
        self.v2a_devices = "Flair Devices"
        self.v2a_address = "Address"
        self.v2a_ctime = "Last Updated"
        self.v2a_confirm = "How would you like to proceed?"
        self.v2a_time_format = "%A, %B %-d, %Y %-I:%M %p"

        # V2B INCOMPLETE STRUCTURE DIALOG
        self.v2b_incomplete_msg = (
            "It looks like you were recently working on but did not complete setup of"
        )

        # DELETE HOME DIALOG

        self.delete_home_title = "Are You Sure?"
        self.delete_home_graf_one = "Deleting <HOME> will not remove the 0 Flair vents and 1 Flair pucks from the home. You will need to manually remove them before you can add them to a new home."
        self.delete_home_graf_two = "Don’t worry if there are minor issues with setup so far, you can easily fix them after setup is complete!"
        self.delete_home_confirm = (
            "Are you sure you want to abandon setup and delete <HOME>?"
        )
        self.kb_link_text = "Learn More"
        self.kb_article_reset_devices_url = (
            "https://support.flair.co/hc/en-us/articles/12356472445709"
        )

        # DELETE USER DIALOG

        self.delete_user_subheader = "This action will permanently delete all data associated with your account. This includes any Homes you have created that only this account has access to."
        self.delete_user_title = "Delete Your Account?"
        self.delete_user_para_1_text = "This action will permanently delete all data associated with your account. This includes any Homes you have created that only this account has access to."
        self.delete_user_bold_text = "There will be no way to restore your account."

        # TEMPERATURE CALIBRATION TOOLTIP

        self.tempcal_tooltip_title = "Self Temperature Calibration Tips"
        self.tempcal_para_1_title = "Time to Equilibrate"
        self.tempcal_para_1_text = "Pucks need time to self calibrate. Please wait about 15 minutes after powering on a puck to allow temperatures to stabilize before applying new temperature offsets"
        self.tempcal_para_2_title = "Placement"
        self.tempcal_para_2_text = "For an accurate room temperature, place pucks away from direct airflow from vents, fans, IR devices, etc"

        # SEP 2023 ADD FLAIR DEVICE WIZARD

        self.add_flair_device_add_puck = "Add a Gateway Puck or Sensor Pucks"

        # OTHER NAV

        self.setup_create_new_room = "Create a new room"
        self.setup_create_new_home = "Create Home"
        self.setup_plug_in_puck = "Plug in your Puck"
        self.setup_select_thermostat = "Select your Thermostat"
        self.setup_what_to_control = "What do you want Flair to control?"
        self.setup_mode_enable = "Switching to Setup Mode"
        self.setup_mode_active = "Structure in Setup Mode."
        self.setup_mode_end = "Done with Setup?"

        # CONTROL BAR POPOVER PRIMARY TEXTS
        self.control_popover_text = {
            "home_away": ["Home", "Away"],
            "set_point": ["Set Point for Home"],
            "system_mode": ["Auto", "Manual"],
            "heat_cool_mode": ["Heat", "Cool", "Auto Heat/Cool", "Off"],
            "schedule": ["No Schedule", "Create New Schedule"],
        }

        # WEATHER RESPONSE PAYLOADS

        self.weather_payload_hot_partly_cloudy = {
            "data": {
                "type": "weather-readings",
                "attributes": {
                    "condition": "Clouds",
                    "humidity": 27.0,
                    "wind-direction": 130.0,
                    "outside-temperature-c": 32.1,
                    "pressure": 1016.0,
                    "cloud-cover": 40,
                    "wind-chill": None,
                    "windspeed": 3.6,
                },
                "id": "0b9c48da-dc53-41af-bccf-1a3a50142912",
            },
        }

        # PLUS MENU ITEMS
        self.config_secondary_heat = "Configure Secondary Heat"
        self.add_gateway = "Add new Gateway Puck"
        self.add_sensor = "Add new Sensor Puck"
        self.add_puck = "Add a Flair Puck"
        self.add_vent = "Add a Flair Smart Vent"
        self.add_thermostat = "Add new Thermostat"
        self.add_ir_device = "Add new Mini Split or IR Device"
        self.add_user = "Add new User to Home"
        self.add_room = "Add new Room"
        self.add_home = "Add New Home"
        # TODO: Add these to the list when ui PR-922 merged
        # (self.add_puck, self.add_flair_device_add_puck),
        # (self.add_vent, self.setup_mode_enable),
        self.standard_plus_menu_items = [
            (self.add_thermostat, self.setup_select_thermostat),
            (self.add_ir_device, self.setup_what_to_control),
            (self.add_user, "Invite User"),
            (self.add_room, self.setup_create_new_room),
            (self.add_home, self.setup_create_new_home)
        ]
