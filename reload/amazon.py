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
    reload = "gcui-asv-reload-form-custom-amount",
    buynow = "buyNow_feature_div",
    usr = "ap_email",
    pwd = "ap_password",
    cont = "continue",
    submit = "signInSubmit"
)
"""Amazon HTML IDs."""

_DRIVER = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=webdriver.ChromeOptions()
)
"""Google Chrome web driver install and init."""


@dataclass
class Amazon:
    username: str
    password: str
    card: str


    def _wait_for_sign_in(self, timeout: float) -> None:
        logger.debug("Waiting for sign in page to load.")
        WebDriverWait(_DRIVER, timeout).until(EC.title_contains("Amazon Sign-In"))


    # TODO: add ability to prompt user to confirm before clicking buy now
    def reload_balance(self, amount: float) -> bool:
        if amount < 0.5:
            raise ValueError("'amount' must be >= 0.5")
        # Navigate to reload URL
        logger.info(f"Navigating to '{_URL}'")
        _DRIVER.get(_URL)

        # Sign in with username and password
        logger.info("Entering credentials.")
        self._wait_for_sign_in(10)
        _DRIVER.find_element(By.ID, _ID["usr"]).send_keys(self.username)
        _DRIVER.find_element(By.ID, _ID["cont"]).click()

        self._wait_for_sign_in(10)
        _DRIVER.find_element(By.ID, _ID["pwd"]).send_keys(self.password)
        _DRIVER.find_element(By.ID, _ID["submit"]).click()

        # Add balance and submit
        logger.info(f"Reloading gift card balance with ${amount}.")
        _DRIVER.find_element(By.ID, _ID["reload"]).send_keys(amount)
        _DRIVER.find_element(By.ID, _ID["buynow"]).click()

        return True
