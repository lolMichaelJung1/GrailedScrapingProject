import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
#The issue is that this script is taking in all designers from Grailed. Somehow I need to narrow it down to a select # of designers
#to reduce runtime. I filtered it to ignore brands with less than 1000 listings but for some reason the script is iterating through ALL 
#designers on grailed
#set designer you want to scrape
target_designer = 'Rick Owens'
# Setting a base URL for where to find all the designers on Grailed
base_url = "https://www.grailed.com/designers/"

# Open up Chrome
chrome_options = Options()
chrome_options.add_argument("--start-maximized")  # Using full screen
driver = webdriver.Chrome(service=Service(executable_path="chromedriver.exe"), options=chrome_options)
driver.get(base_url)

# Wait for 30 seconds, will quit if it takes over 30 seconds
timeout = 30
try:
    WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((By.XPATH, "//div[@id='app']")))
except TimeoutException:
    print("Timed out")
    driver.quit()

# Gathering all links on the designer page (look into this)
results = driver.find_elements(By.XPATH, "//a[@href]")

# Making a list of all the links
Link = []
for result in results:
    link = result.get_attribute("href")  # Grabbing the link attribute
    Link.append(link)

# Turn the Links into a DataFrame
ItemDF = pd.DataFrame(Link, columns=['Link'])

# Filtering out links that are not designer page links
ItemDF = ItemDF[ItemDF['Link'].str.contains("designers/")]
# List of sold links to be appended to
sold_links = []

# Reusing the existing Chrome instance for designer links
for link in ItemDF['Link']:
    # Will open the designer link
    driver.get(link)

    # Wait for 30 seconds
    timeout = 30
    try:
        WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((By.XPATH, "//div[@id='__next']")))
    except TimeoutException:
        print("Timed out waiting for the page to load")
        continue

    WebDriverWait(driver, 10)

    try:
        element = driver.find_elements(By.XPATH,"//*[contains(text(),'Show Only')]")  # Finding the show-only button
        element[0].click()  # Clicking show-only
    except:
        continue

    driver.implicitly_wait(1)

    try:
        elem = driver.find_element(By.XPATH, "//div[@class='UsersAuthentication']")  # User login window will pop up
        ac = ActionChains(driver)
        ac.move_to_element(elem).move_by_offset(250, 0).click().perform()  # Clicking away from the login window
    except:
        print('failed')
        continue

    driver.implicitly_wait(1)

    try:
        element = driver.find_elements(By.XPATH,"//*[contains(text(),'Show Only')]")  # Finding the show-only button again
        element[0].click()  # Clicking now that the pop-up is away
    except:
        continue

    driver.implicitly_wait(1)

    try:
        element = driver.find_elements(By.XPATH,"//input[@id='sold-filter']")  # Finding the sold box
        element[0].click()  # Click sold box
    except:
        continue

    driver.implicitly_wait(1)

    try:
        sold_link = driver.current_url  # Getting the current URL, which is the sold link for the designer
        sold_links.append(sold_link)  # Appending sold link
    except:
        continue

# Reusing the existing Chrome instance for sold links
Link = []
for link in sold_links:
    try:
        # Set a URL
        driver.get(link)

        # Wait 30 seconds
        timeout = 30
        WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((By.XPATH, "//div[@class='feed-item']")))
    except TimeoutException:
        print("Timed out waiting for the page to load")
        continue

    try:
        ScrollCount = 0
        # Getting the number of items on the page. If it is a full page, then it will be 40
        results = driver.find_elements(By.XPATH, '//div[@class="FiltersInstantSearch"]//div[@class="feed-item"]')
    except Exception as e:
        print(e)
        continue

    # If the number of items is less than 25 sold, we will not be collecting that data 
    if len(results) < 1000:
        continue

    # While the page is full, will continue to scroll up to a maximum of 4 scrolls
    try:
        while (len(results) % 40 == 0) and (ScrollCount < 4):
            driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
            ScrollCount += 1
            results = driver.find_elements(By.XPATH,'//div[@class="FiltersInstantSearch"]//div[@class="feed-item"]')
            time.sleep(1)
    except Exception as e:
        print(e)
        continue

    # For each item link in results, will get the link and append to link list
    try:
        for result in results:
            link = result.find_element(By.XPATH,'./a').get_attribute("href")
            Link.append(link)
    except Exception as e:
        print(e)
        continue

# Turn the lists into a DataFrame and save
ItemLinks = pd.DataFrame(Link, columns=['Link'])

# Empty lists for all the information I want to gather
UserName = []
Designer = []
SubTitle = []
SizeColorCond = []
Category = []
FeedbackCount = []
Price = []
Description = []
NumImages = []
Link = []

# Reusing the existing Chrome instance for item details
driver.get("https://www.grailed.com/sold")
# Timeout after 30 seconds
timeout = 30
try:
    WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((By.XPATH, "//div[@class='feed-item']")))
except TimeoutException:
    print("Timed out waiting for the page to load")
    driver.quit()

# Looping through all the links in ItemLinks
for link in ItemLinks['Link']:
    try:
        driver.get(link)
    except:
        continue

    # Gathering item designer name
    try:
        designer = driver.find_elements(By.XPATH,'//a[@class="designer-name"]')
        if len(designer) == 2:
            Designer.append(f'{designer[0].text} x {designer[1].text}')  # If the item is a collaboration between designers
        else:
            Designer.append(designer[0].text)
    except:
        Designer.append("")

    # Gathering item sub-title
    try:
        sub_title = driver.find_element(By.XPATH,'//h1[@class="listing-title sub-title"]').text
        SubTitle.append(sub_title)
    except:
        SubTitle.append("")

    # Gathering poster's username
    try:
        user_name = driver.find_element(By.XPATH,'//span[@class="-username"]').text
        UserName.append(user_name)
    except:
        UserName.append("")

    # Gathering poster's feedback count
    try:
        feedback_count = driver.find_element(By.XPATH,'//span[@class="-feedback-count"]').text
        FeedbackCount.append(feedback_count)
    except:
        FeedbackCount.append("")

    # Gathering item size, color, and condition
    try:
        sizecolorcond = driver.find_elements(By.XPATH,'//h2[@class="listing-size sub-title"]')
        s_scc = ""
        for part in sizecolorcond:
            s_scc += " " + part.text
        SizeColorCond.append(s_scc)
    except:
        SizeColorCond.append("")

    # Gathering the sold price of the item
    try:
        item_price = driver.find_element(By.XPATH,'//h2[@class="-price _sold"]').text
        Price.append(item_price)
    except:
        Price.append("")

    # Gathering the description of the item
    try:
        item_description = driver.find_element(By.XPATH,'//div[@class="listing-description"]').text
        Description.append(item_description)
    except:
        Description.append("")

    # Gathering the total number of images for the item
    try:
        num_images = driver.find_elements(By.XPATH,'//div[@class="-image-wrapper -thumbnail"]')
        NumImages.append(len(num_images))
    except:
        NumImages.append(0)

    # Gathering the category of the item
    try:
        item_category = driver.find_elements(By.XPATH,'//a[@class="-crumb "]')
        if len(item_category) > 2:
            Category.append(item_category[2].text)
        else:
            Category.append(item_category[1].text)
    except:
        Category.append("")

    try:
        Link.append(link)
    except:
        Link.append("")

# Saving the final df
item_desc = pd.DataFrame(
    {'username': UserName,
     'sold_price': Price,
     'designer': Designer,
     'category': Category,
     'description': Description,
     'sub_title': SubTitle,
     'image_count': NumImages,
     'size_color_cond': SizeColorCond,
     'feedback_count': FeedbackCount,
     'link': Link
     })

item_desc.to_csv('item_desc.csv')

# Quit the Chrome driver
driver.quit()

