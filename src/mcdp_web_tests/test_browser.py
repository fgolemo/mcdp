
from selenium import webdriver

from mcdp.logs import logger


class BrowserTest(object):
    def __init__(self):
        
        self.driver = webdriver.PhantomJS() # or add to your PATH
        self.driver.set_window_size(1024, 768) # optional

        self.n = 0
        
    def click_css(self, t):
        e = self.driver.find_element_by_css_selector(t)
        e.click()
        self.screenshot()
    
    def click_partial_link_text(self, t):
        sbtn = self.driver.find_element_by_partial_link_text(t)
        sbtn.click()
        self.screenshot()
        
    def screenshot(self):
        self.driver.save_screenshot('screens/%02d.png' % self.n)
        self.n += 1
    
    def go(self):
        url ='http://127.0.0.1:8080/repos/bundled/shelves/unittests/libraries/basic/models/minus_r_real3/views/dp_graph/'
        self.driver.get(url)
        self.screenshot()
        
        self.driver.get('http://127.0.0.1:8080/')
        self.screenshot()
        
        self.click_partial_link_text('login')
        driver = self.driver
        
        # fill log in screen
        e = driver.find_element_by_css_selector('input[name=login]')
        e.send_keys("andrea")
        e = driver.find_element_by_css_selector('input[name=password]')
        e.send_keys("editor")
        es = driver.find_elements_by_css_selector('button')
        if len(es) > 1:
            msg = 'There should not be more than 1 button'
            logger.error(msg)
        es[1].click()

        # go to shelves        
        self.click_partial_link_text('shelves')
        
        self.click_partial_link_text('unittests')
        self.click_partial_link_text('basic')
        self.click_partial_link_text('minus_real3')
        
        self.click_css('button#size-plus')
        self.click_css('button#size-plus')
        self.click_css('button#size-plus')
        
#         self.click_partial_link_text('activate')


if __name__ == '__main__':
    bt = BrowserTest()
    bt.go()
    