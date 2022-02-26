"""Reload Amazon gift card balance."""

import logging

from dataclasses import dataclass

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)

_URL: str = "https://www.amazon.com/asv/reload/"
"""Amazon URL for purchasing gift card reloads."""

_ID: dict = dict(
    auth_code = "auth-mfa-otpcode",
    buynow = "buyNow_feature_div",
    cont = "continue",
    pwd = "ap_password",
    reload = "gcui-asv-reload-form-custom-amount",
    signin_auth = "auth-signin-button",
    signin = "nav-link-accountList",
    submit = "signInSubmit",
    usr = "ap_email"
)
"""Amazon HTML IDs."""


# TODO: when there are multiple purchases, provide option to leave browser open
class Amazon:
    """"""


    def __init__(self, username: str, password: str, card: str) -> None:
        self.username = username
        self.password = password
        self.card = card

        # Create driver and navigate to sign-in page
        logger.debug("Creating Chrome driver")
        self._DRIVER = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=webdriver.ChromeOptions()
        )

        # Sign in
        self._sign_in()

    #def _wait(self, title: Optional[str] = None, timeout: float = 10) -> None:
    #    if title:
    #        logger.debug(f"Waiting for page to load with title '{title}'")
    #        WebDriverWait(self._DRIVER, timeout).until(EC.title_contains(title))
    #    else:
    #        now = datetime.now()
    #        while True:
    #            self._DRIVER.title
    #            time.sleep(0.25)


    def _sign_in(self) -> None:#, timeout: float) -> None:
        # Navigate to Amazon go to sign in page
        amzn_home = "https://www.amazon.com/"
        logger.debug(f"Navigating to Amazon '{amzn_home}'")
        self._DRIVER.get(amzn_home)
        self._DRIVER.find_element(By.ID, _ID["signin"]).click()

        #TODO: might need to wait for page title "Amazon Sign-In" using _wait()
        #TODO: might need to add some waits so amazon doesn't flag or reject log in
        # Sign in with username and password
        logger.info("Entering credentials.")
        #self._wait_for_sign_in(10)
        self._DRIVER.find_element(By.ID, _ID["usr"]).send_keys(self.username)
        self._DRIVER.find_element(By.ID, _ID["cont"]).click()

        #self._wait_for_sign_in(10)
        self._DRIVER.find_element(By.ID, _ID["pwd"]).send_keys(self.password)
        self._DRIVER.find_element(By.ID, _ID["submit"]).click()

        # Check for OTP/Multi factor auth and prompt user for info
        title = self._DRIVER.title
        logger.debug(f"Page title after entering password is '{title}'")
        if title == "Amazon Sign-In":
            logger.info("OTP/multifactor authentication requested")
            otp = input("Please enter the OTP code sent to you: ")
            self._DRIVER.find_element(By.ID, _ID["auth_code"]).send_keys(otp)
            self._DRIVER.find_element(By.ID, _ID["signin_auth"]).click()
        else:
            logger.debug("No OTP/two-factor authentication requested.")


    # TODO: add ability to prompt user to confirm before clicking buy now
    def reload_balance(self, amount: float) -> bool:
        #if amount < 0.5:
        #    raise ValueError("'amount' must be >= 0.5")

        # Go to reloads page
        amzn_reload = "https://www.amazon.com/asv/reload/"
        logger.debug(f"Navigating to Amazon '{amzn_reload}'")
        self._DRIVER.get(amzn_reload)

        # Add balance and submit
        logger.info(f"Reloading gift card balance with ${amount}.")
        self._DRIVER.find_element(By.ID, _ID["reload"]).send_keys(amount)
        self._DRIVER.find_element(By.ID, _ID["buynow"]).click()

        return True
