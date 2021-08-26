import os
import schedule
import time
import datetime
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

# Links for Today's Album & Track
# opts = Options()
# opts.headless = True
# driver = webdriver.Firefox(options=opts)
# driver.get('https://ra.co/')
# album = driver.find_element_by_xpath('//*[@id="__next"]/div[5]/section[2]/div[2]/div/section[1]/ul/li[1]/div/h3/a/span')
# track = driver.find_element_by_xpath('//*[@id="__next"]/div[5]/section[2]/div[2]/div/section[1]/ul/li[3]/div/h3/a/span')
# album_link = album.get_attribute('href')
# track_link = track.get_attribute('href')
# print(album_link, track_link)
# driver.quit()
def main():
    print("Starting RA scrape...")
    today = str(datetime.datetime.now())
    today_date = today[:10]
    today_day = today[8:10]
    print(today_date)

    opts = Options()
    opts.headless = True
    driver = webdriver.Firefox(options=opts)
    driver.get(f'https://ra.co/events/us/newyork?week={today_date}')
    driver.implicitly_wait(10)

    events = []

    def scrape():
        body = driver.find_element_by_xpath('//*[@id="__next"]/div[4]/section[1]/div/div/div[2]')
        anchors = body.find_elements_by_tag_name('a')
        print(f"Anchors found: {len(anchors)}")
        stale = 0
        for i in anchors:
            try:
                if not i.text:
                    continue
                href = i.get_attribute('href')
            except StaleElementReferenceException:
                print(f"Stale Element")
                return False
            if 'events' in href and not 'tickets' in href and not 'us' in href:
                events.append(href)
        return True

    check = scrape()
    while not check:
        print("Too many stale elements, restarting loop in 3 secs...")
        time.sleep(3)
        check = scrape()

    print(f"Events: {len(events)}")

    meta = []
    # Meta per show
    for e, j in enumerate(events):
        driver.get(j)
        try:
            venue = driver.find_element_by_xpath('//*[@id="__next"]/header/div/div[2]/div[2]/div/ul/li[1]/div')
            venue_name = venue.find_element_by_tag_name('a')
            venue_name = venue_name.text
            address = venue.find_element_by_tag_name('li')
            address = address.text
        except NoSuchElementException or StaleElementReferenceException:
            venue_name = "Review Link for Venue"
            address = "Review Link for Address"
        try:
            showtime = driver.find_element_by_xpath('//*[@id="__next"]/header/div/div[2]/div[2]/div/ul/li[2]/div/div[2]')
            date = showtime.find_element_by_tag_name('a')
            date = date.text
            showtime = showtime.find_element_by_tag_name('div')
            showtime = showtime.text
        except NoSuchElementException or StaleElementReferenceException:
            date = "Review Link for Date"
            showtime = "Review Link for Showtime"
        try:
            lineup = driver.find_element_by_xpath('//*[@id="__next"]/section[1]/div/section[1]/div/div/div[2]/ul/li[1]/div/span')
            lineup = lineup.text
            lineup = lineup.replace('\n',' | ')
        except NoSuchElementException or StaleElementReferenceException:
            lineup = "Review Link for Lineup"
        show_deets = [date, lineup, venue_name, showtime, address, j]
        for deets in show_deets:
            print(deets)
        print("--- --- --- --- --- --- --- --- --- --- --- ")
        meta.append(show_deets)
        # if e == 5:
        #     break

    # os.system("taskkill /IM firefox.exe /F")

    # opts = Options()
    # opts.headless = False
    # driver = webdriver.Firefox(options=opts)
    driver.get('https://www.memetides.com/t/ra-co-on-memetides/926')
    login = driver.find_element_by_xpath('/html/body/section/div/div[1]/header/div/div/div[2]/span/button[2]')
    login.click()
    username = driver.find_element_by_id('login-account-name')
    username.send_keys('ilovemycat666')
    password = driver.find_element_by_id('login-account-password')
    password.send_keys('dCDR5h7694JCJ74qXDAN')
    login_button = driver.find_element_by_xpath('//*[@id="login-button"]')
    login_button.click()
    time.sleep(1)
    button = driver.find_elements_by_tag_name('button')
    def edit():
        edits = []
        for b in button:
            title = b.get_attribute('title')
            if title == 'edit this post':
                edits.append(b)
        return edits
    edits = edit()
    while not edits:
        time.sleep(2)
        edits = edit()
        print(len(edits))

    print(len(edits))
    edits[1].click()

    time.sleep(.5)
    textarea = driver.find_element_by_tag_name('textarea')
    textarea.clear()
    textarea.send_keys('<table>')
    for me in meta:
        if me[4] == "Review Link for Address":
            maps = "ra.co"
        else:
            maps = me[4].replace(" ", '+')
            maps = "https://google.com/maps/dir/" + maps
        textarea.send_keys(f'''    <tr>
          <td><strong>Date:</strong><td>
          <td>{me[0]}</td>
        </tr>
        <tr>
          <td><strong>Linup:</strong><td>
          <td>{me[1]}</td>
        </tr>
        <tr>
          <td><strong>Venue:</strong><td>
          <td>{me[2]}</td>
        </tr>
        <tr>
          <td><strong>Time:</strong><td>
          <td>{me[3]}</td>
        </tr>
        <tr>
          <td><strong>Place:</strong><td>
          <td><a href="{maps}">{me[4]}</a></td>
        </tr>
        <tr>
          <td><strong>More:</strong><td>
          <td><a href="{me[5]}">ra.co</a></td>
        </tr>
        <tr>
          <td>-</td>
        </tr>''')
    textarea.send_keys('</table>')
    time.sleep(.5)
    button = driver.find_elements_by_tag_name('button')
    for b in button:
        title = b.get_attribute('title')
        if title == 'Or press Ctrl+Enter':
            b.click()
            print('message posted')
            break
    print('closing in 20secs...')
    time.sleep(20)
    os.system("taskkill /IM firefox.exe /F")

main()
# schedule.every().day.at("09:00").do(main)
#
# while True:
# 	schedule.run_pending()
# 	time.sleep(59)
# print(f'''
# <tr>
#   <td><strong>Date:</strong><td>
#   <td>{date}</td>
# </tr>
# <tr>
#   <td><strong>Linup:</strong><td>
#   <td>{lineup}</td>
# </tr>
# <tr>
#   <td><strong>Venue:</strong><td>
#   <td>{venue_name}</td>
# </tr>
# <tr>
#   <td><strong>Time:</strong><td>
#   <td>{showtime}</td>
# </tr>
# <tr>
#   <td><strong>Time:</strong><td>
#   <td>{address}</td>
# </tr>
# <tr>
#   <td><strong>Link:</strong><td>
#   <td>{j}</td>
# </tr>
# ''')



# print(f"Date:\t{date}")
# print(f"Lineup:\t{lineup}")
# print(f"Venue:\t{venue_name}")
# print(f"Time:\t{showtime}")
# print(f"Adrs:\t{address}")
# print(f"Link:\t{j}")
# print("")
