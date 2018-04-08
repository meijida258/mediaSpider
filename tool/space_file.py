import requests

from selenium import webdriver

driver = webdriver.PhantomJS()
driver.get('https://music.163.com/m/artist?id=159300')
driver.switch_to.frame('contentFrame')
# print(driver.find_element_by_id('5366223041522828275882').text)

print(driver.page_source)
print(driver.current_url)
driver.close()
