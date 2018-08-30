# -*- coding: utf-8 -*-
import random

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time, re



class Kr_36():


    def __init__(self):
        self.op = webdriver.ChromeOptions()
        # self.op.add_extension('/Users/hush/Downloads/katalon.crx')
        # self.op.add_extension('/Users/hush/Downloads/chrome-data-kr36.crx')
        self.op.add_extension('/Users/hush/Codes/tshbao/tool/kr36/chrome-data-kr36.crx')
        self.op.add_argument('--auto-open-devtools-for-tabs')
        self.driver = webdriver.Chrome(executable_path="/Users/hush/Downloads/chromedriver", chrome_options=self.op)
        self.driver.implicitly_wait(30)
        self.driver.set_page_load_timeout(30)
        self.base_url = "https://rong.36kr.com/list/detail&"
        self.verificationErrors = []
        self.accept_next_alert = True

    def to_run(self):
        driver = self.driver
        try:
            driver.get("https://rong.36kr.com/list/detail&")
            # driver.find_element_by_tag_name("body").send_keys(Keys.COMMAND + Keys.ALT + 'i')
            try:
                driver.find_element_by_xpath("/html/body/header/div/div[3]/span").click()
            except:
                pass
            time.sleep(random.randint(1, 2))
            driver.find_element_by_id("kr-shield-username").click()
            time.sleep(random.randint(1, 2))
            driver.find_element_by_id("kr-shield-username").clear()
            driver.find_element_by_id("kr-shield-username").send_keys("guo_hush@163.com")
            time.sleep(random.randint(1, 2))
            driver.find_element_by_id("kr-shield-password").clear()
            driver.find_element_by_id("kr-shield-password").send_keys("zhufu2015.")
            time.sleep(random.randint(1, 2))
            driver.find_element_by_id("kr-shield-submit").click()
            time.sleep(random.randint(1, 2))
            # driver.find_element_by_xpath("//*[@id=\"sidebarNav\"]/dl[2]/dd[1]/a").click()
            driver.find_element_by_xpath(
                "(//*[@id=\"projectListContainer\"]/div[1]/div[2]/table/tbody/tr[2]/td[1]/a)").click()

            # time.sleep 强制等待
            # # time.sleep(random.randint(20))
            # WebDriverWait 显式等待
            # # locator = (By.ID, 'cloumn3ProjectList')
            # # ele = WebDriverWait(driver,20).until(EC.presence_of_element_located(locator))
            # implicitly_wait 隐式等待

            # 滑动滚动条方法 注释的经测试无效...
            # # target = driver.find_elements_by_xpath('//*[@id=\"cloumn3ProjectList\"]/ul/li[10]/a')
            # # driver.execute_script("arguments[0].scrollIntoView();", target)
            # # js = 'document.getElementsByClassName("ps-scrollbar-y").scrollTop=155'
            # # driver.execute_script(js)
            # # time.sleep(2)
            # ele = driver.find_element_by_xpath("//*[@id=\"cloumn3ProjectList\"]/ul/li[5]/a")
            # ele.location_once_scrolled_into_view
            #
            # # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # # for i in range(5):
            # # driver.find_element_by_xpath("//div[@id=\"cloumn3ProjectList\"]/ul/li[5]/a").send_keys(Keys.DOWN)
            # js = 'document.getElementsByClassName("ps-scrollbar-y-rail").scrollTop=10000'
            # driver.execute_script(js)
            # target = driver.find_element_by_xpath("//div[@id=\"cloumn3ProjectList\"]/ul/li[10]")
            # driver.execute_script("arguments[0].scrollIntoView();", target)
            # js = "var q=document.body.scrollTop=100000"
            # driver.execute_script(js)

            for i in range(2,21):
                try:
                    driver.find_element_by_xpath("//*[@id=\"cloumn3ProjectList\"]/ul/li[%d]/a"%i).click()
                    # driver.find_element_by_xpath("//*[@class=ps-scrollbar-y").send_keys(Keys.DOWN)
                    ActionChains(driver).send_keys(Keys.PAGE_DOWN).perform()
                    time.sleep(random.randint(1, 3))
                except:
                    continue

            time.sleep(10)
        except:
            pass
        driver.close()
        driver.quit()


    def is_element_present(self, how, what):
        try:
            self.driver.find_element(by=how, value=what)
        except NoSuchElementException as e:
            return False
        return True


    def is_alert_present(self):
        try:
            self.driver.switch_to_alert()
        except NoAlertPresentException as e:
            return False
        return True


    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally:
            self.accept_next_alert = True


    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)


if __name__ == "__main__":
    unittestest = Kr_36()
    unittestest.to_run()