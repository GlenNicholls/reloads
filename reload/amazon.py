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


@dataclass
class Amazon:
    username: str
    password: str
    card: str


    def _wait_for_sign_in(self, timeout: float) -> None:
        logger.debug("Waiting for sign in page to load.")
        WebDriverWait(self._driver, timeout).until(EC.title_contains("Amazon Sign-In"))


    def _add_balance(self, amount: float) -> None:
        # Add balance and submit
        if amount >= 0.5:
            self._driver.find_element(By.ID, _ID["reload"]).send_keys(amount)
            self._driver.find_element(By.ID, _ID["buynow"]).click()
        else:
            raise ValueError("'amount' must be >= 0.5")

        # Sign in with username and password
        logger.info("Entering credentials.")
        self._wait_for_sign_in(10)
        self._driver.find_element(By.ID, _ID["usr"]).send_keys(self.username)
        self._driver.find_element(By.ID, _ID["cont"]).click()

        self._wait_for_sign_in(10)
        self._driver.find_element(By.ID, _ID["pwd"]).send_keys(self.password)
        self._driver.find_element(By.ID, _ID["submit"]).click()


    def reload_balance(self, amount: float) -> None:
        logger.info(f"Reloading gift card balance with ${amount}.")

        # Configure driver
        self._driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=webdriver.ChromeOptions()
        )

        # Navigate to reload URL
        self._driver.get(_URL)

        # Add balance
        self._add_balance(amount)


if __name__ == "__main__":
    amzn = Amazon("dkillers303@gmail.com", "bar")
    amzn.reload_balance(0.5)