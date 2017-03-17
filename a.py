from splinter import Browser

with Browser('chrome') as browser:
    # Visit URL
    url = "http://127.0.0.1:8080/"
    browser.visit(url)
    # Find and click the 'search' button
    link = browser.find_link_by_partial_text('login')
    print link
    link.click()
    # button = browser.find_by_name('btnG')
    # # Interact with elements
    # button.click()
    # if browser.is_text_present('splinter.readthedocs.io'):
    #     print("Yes, the official website was found!")
    # else:
    #     print("No, it wasn't found... We need to improve our SEO techniques")
