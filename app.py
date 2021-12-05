from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium_stealth import stealth
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
import datetime
import numpy as np
import csv
import pandas as pd
import re
from PIL import Image
from io import BytesIO
import requests
def take_screenshot(element, driver, filename='screenshot.png'):
  location = element.location_once_scrolled_into_view
  size = element.size
  png = driver.get_screenshot_as_png() # saves screenshot of entire page
  im = Image.open(BytesIO(png)) # uses PIL library to open image in memory
  left = location['x']
  top = location['y']
  right = location['x'] + size['width']
  bottom = location['y'] + size['height']
  im = im.crop((left, top, right, bottom)) # defines crop points
  im.save(filename) # saves new cropped image


#Shuttle User Agent To Reduce chance getting detected
software_names = [SoftwareName.CHROME.value]
operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]   
user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)
# Get list of user agents.
user_agents = user_agent_rotator.get_user_agents()
# Get Random User Agent String.
user_agent = user_agent_rotator.get_random_user_agent()


path_to_extension = r'C:\Users\your-user-name\AppData\Local\Google\Chrome\User Data\Default\Extensions\your-chrome-extension-hash\5.8_0'
option = webdriver.ChromeOptions()
option.add_argument("--disable-infobars")
option.add_argument("start-maximized")
#option.add_argument("--headless")     #to see how Selenium works, uncomment this
option.add_argument("--no-sandbox")
option.add_argument("--window-size=1420,5080")
option.add_argument("--disable-gpu")
option.add_argument("--disable-popup-blocking")
option.add_argument("--f'user-agent={user_agent}")
option.add_argument("load-extension=" + path_to_extension)

capabilities = option.to_capabilities()
capabilities = {
   'browser': 'chrome',
   'browser_version': 'latest',
   'os': 'Windows',
   'os_version': '10',
   'build': 'Python Sample Build',
   'name': 'Pop-ups testing'
}
capabilities["chromeOptions"] = {}
capabilities["chromeOptions"]["excludeSwitches"] = ["disable-popup-blocking"]
# Pass the argument 1 to allow and 2 to block
option.add_experimental_option("prefs", { 
    "profile.default_content_setting_values.notifications": 1 
})
driver = webdriver.Chrome(options = option , desired_capabilities=capabilities)
# Selenium Stealth settings
driver.get("https://mraovat.nguoi-viet.com/default.aspx")



#user_agent_selenium = driver.execute_script("return navigator.userAgent;")
#print(user_agent_selenium)    #for debuggin, print out user_agent

nail_job_page =  driver.find_element_by_css_selector("div.wrapper:nth-child(3) div.mainBody:nth-child(4) div.pageContent:nth-child(5) table.NVCatListingsBody tr:nth-child(1) td.NVcol1:nth-child(1) p.even:nth-child(10) a:nth-child(1) > b:nth-child(1)")
nail_job_page.click()
#driver.implicitly_wait(3)
jobs_post = driver.find_elements_by_css_selector("a[id^=ctl00_PageContent_FeaturedListings_Listings_ct][id$=ListingTitle]")
featured_post = driver.find_elements_by_css_selector("img[id^=ctl00_PageContent_FeaturedListings][id$=Image2]")
print("Length = " + str(len(featured_post)))



#Prepare empty lists to populate data 
temp = np.array(np.zeros(len(featured_post))) 
jobs_arr= np.empty(len(featured_post), dtype=object)
phone_arr = np.empty(len(featured_post), dtype=object)
links_arr = np.empty(len(featured_post), dtype=object)
city_arr = np.empty(len(featured_post), dtype=object)
state_arr = np.empty(len(featured_post), dtype=object)
corrected_phn_arr = np.empty(len(featured_post), dtype=object)
regex= "\w{3}-\w{3}-\w{4}"  #Regex for phone, basic

for i in range(len(featured_post)):
    #print(jobs_post[i].text) #Debug
    jobs_arr[i] = jobs_post[i].text
    links_arr[i] = jobs_post[i].get_attribute('href')
    if re.search(regex, jobs_arr[i]):
       phone_arr[i] = re.search(regex, jobs_arr[i]).group()
       
    else:
        print("Invalid phone number")
        try:
            temp_link = jobs_post[i].get_attribute('href')
            jobs_post[i].send_keys(Keys.CONTROL + 't')
            driver2 = webdriver.Chrome(options = option)
            driver2.get(temp_link)
            #print("link=" + temp_link)   #Debug
            driver2.implicitly_wait(3)
            driver2.save_screenshot("screenshot.png") 
            description = driver2.find_element_by_css_selector("div#ctl00_PageContent_Tab_Description_content_DescriptinDiv>div:nth-child(2)")
            print(description.text)
            phone_arr[i] = re.search(regex,description.text).group()
            print("======rescrawled successfully======")
            driver2.close()
        except:
            print("======rescrawled not successfully======")
    
    try:
        response = requests.get('http://localhost:5000/codes?code=' + phone_arr[i][0:3])
        response_data = response.json()
        city_arr[i] = response_data['City']
        state_arr[i] = response_data['State']
    except :
        city_arr[i] = "unknown"
        state_arr[i] = "unknown"

dictOfWords = { i :  jobs_post[i] for i in range(0, len(jobs_post) ) }
fn = {"id","fieldsname"}


#Final Step: Prepare for output
time_stamp =  datetime.datetime.now().strftime("%DD%MM").replace('/','')
#print(time_stamp) #Debugg
#Output file will have 5 columns: id, phone_number, city, state, url
mydict = {"id": jobs_arr,"phone_number" :phone_arr , "city": city_arr, "state": state_arr, "url": links_arr}
df = pd.DataFrame(mydict)
file_name =  "featured_new_listings" + time_stamp +".csv"
print(file_name)
df.to_csv(file_name,index=False)  #export to file
e =  driver.find_element_by_css_selector("a[id^=ctl00_PageContent_FeaturedListings_Listings_ct][id$=ListingTitle]")
take_screenshot(e,driver, 'e.png')  #export to file
print("FINISHING....SUCCESSFULLY") 
driver.close()



