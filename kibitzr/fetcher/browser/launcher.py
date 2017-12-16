"""
FireFox housekeeping - starting and stopping process
"""

import os
import sys
import shutil
import logging
from contextlib import contextmanager


PROFILE_DIR = 'firefox_profile'
logger = logging.getLogger(__name__)
FIREFOX_INSTANCE = {
    'driver': None,
    'headed_driver': None,
}


def cleanup():
    """Must be called before exit"""
    temp_dirs = []
    if FIREFOX_INSTANCE['driver'] is not None:
        if FIREFOX_INSTANCE['driver'].profile:
            temp_dirs.append(FIREFOX_INSTANCE['driver'].profile.profile_dir)
        try:
            FIREFOX_INSTANCE['driver'].quit()
            FIREFOX_INSTANCE['driver'] = None
        except:
            logger.exception(
                "Exception occurred in browser cleanup"
            )
    if FIREFOX_INSTANCE['headed_driver'] is not None:
        if FIREFOX_INSTANCE['headed_driver'].profile:
            temp_dirs.append(FIREFOX_INSTANCE['headed_driver'].profile.profile_dir)
        try:
            FIREFOX_INSTANCE['headed_driver'].quit()
            FIREFOX_INSTANCE['headed_driver'] = None
        except:
            logger.exception(
                "Exception occurred in browser cleanup"
            )
    for temp_dir in temp_dirs:
        shutil.rmtree(temp_dir, ignore_errors=True)


@contextmanager
def firefox(headless=True):
    """
    Context manager returning Selenium webdriver.
    Instance is reused and must be cleaned up on exit.
    """
    from selenium import webdriver
    from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
    if headless:
        driver_key = 'driver'
    else:
        driver_key = 'headed_driver'
    if FIREFOX_INSTANCE[driver_key] is None:
        if logger.level == logging.DEBUG:
            firefox_binary = FirefoxBinary(log_file=sys.stdout)
        else:
            firefox_binary = FirefoxBinary()
        if headless:
            firefox_binary.add_command_line_options('-headless')
        # Load profile, if it exists:
        if os.path.isdir(PROFILE_DIR):
            firefox_profile = webdriver.FirefoxProfile(PROFILE_DIR)
        else:
            firefox_profile = None
        FIREFOX_INSTANCE[driver_key] = webdriver.Firefox(
            firefox_binary=firefox_binary,
            firefox_profile=firefox_profile,
        )
    yield FIREFOX_INSTANCE[driver_key]