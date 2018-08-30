from selenium import webdriver
from selenium.webdriver.common.keys import Keys


url = 'http://weixin.sogou.com/weixin?query=%E8%98%91%E8%8F%87%E8%A1%97'

def generate_cookie():
    driver = webdriver.Firefox()
    driver.get(url)
    assert "Python" in driver.title
    elem = driver.find_element_by_class_name("wx-rb")
    print elem

    # elem.send_keys("pycon")
    # elem.send_keys(Keys.RETURN)
    # assert "No results found." not in driver.page_source
    driver.close()


if __name__ == '__main__':
    generate_cookie()