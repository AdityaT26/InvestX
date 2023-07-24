from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import csv

email = ""
password = ""

def wait(driver, xpath, t = 10):
    try:
        element = WebDriverWait(driver, t).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
    except:
        pass

colNames = []
datesWbt = []

modeAllStrikes = []

def get_table_data(driver, soup):

    cols = len(colNames)
    iters = 0

    Table, temp, temp2 = [], [], []

    callLTProws = soup.findAll(['td'], class_='text-xs-center font-weight-bold body-1 blue--text')
    for i in callLTProws:
        Table.append([i.get_text().strip()])

    row = soup.findAll(['td'], class_='text-xs-center font-weight-bold body-1')
    for i in range(0, len(row)):
        temp.append(row[i].get_text().strip())
        iters+=1
        if iters==cols-2:
            Table[int((i+1)/iters) - 1] += temp
            #print(Table[int((i+1)/iters) - 1], i, iters, temp)
            iters=0
            temp = []

    putLTProws = soup.findAll(['td'], class_='text-xs-center font-weight-bold body-1 orange--text')
    for i in range(0, len(putLTProws)):
        Table[i] += [putLTProws[i].get_text().strip()]

    Table.insert(0, colNames)

    return Table

def main():
    try:

        print("Enter login email: ")
        email = input()
        print("Enter login password: ")
        password = input()

        driver = webdriver.Chrome(executable_path='chromedriver.exe')
        driver.get('https://opstra.definedge.com/strategy-builder')

        loginBt = '//*[@id="app"]/div[46]/div/div/div[3]/button'
        wait(driver, loginBt)
        driver.find_element_by_xpath(loginBt).click()

        emailBox = '//*[@id="username"]'
        pswdBox = '//*[@id="password"]'
        loginBt = '//*[@id="kc-login"]'

        wait(driver, emailBox)

        driver.find_element_by_xpath(emailBox).send_keys(email)
        driver.find_element_by_xpath(pswdBox).send_keys(password)
        driver.find_element_by_xpath(loginBt).click()

        while len(driver.find_elements_by_xpath('//*[@id="kc-content-wrapper"]/div[1]')) == 1:
            driver.execute_script('alert("Enter correct eMail or password. PRESS OK and go back to the shell to do so.");')
            print("Enter login email: ")
            email = input()
            print("Enter login password: ")
            password = input()
            driver.find_element_by_xpath(emailBox).clear()
            driver.find_element_by_xpath(emailBox).send_keys(email)
            driver.find_element_by_xpath(pswdBox).send_keys(password)
            driver.find_element_by_xpath(loginBt).click()

        driver.get('https://opstra.definedge.com/strategy-builder')

        optionChainBar = '//*[@id="app"]/div[62]/main/div/div/div/div/div[3]/div[2]/div[3]/ul/li/div[1]'
        wait(driver, optionChainBar)
        driver.find_element_by_xpath(optionChainBar).click()

        #driver.execute_script("window.scrollTo(0, 2695)")

        htmlcode=(driver.page_source).encode('utf-8')
        soup = BeautifulSoup(htmlcode,features="html.parser")

        thead = soup.findAll(['th'], class_ = 'column text-xs-center font-weight-black subheading')
        for i in thead:
            colNames.append(i.get_text().strip())

        dates = soup.findAll('div', class_ = 'flex xs4 sm2 md1')
        temp = []
        for i in dates:
            temp.append(i.get_text())
        datesBtClass = '//*[@id="app"]/div[62]/main/div/div/div/div/div[3]/div[2]/div[3]/ul/li/div[2]/div[1]/div[1]/button'
        temp2 = []
        for i in range(1, len(temp)+1):
            temp2.append(driver.find_element_by_xpath('//*[@id="app"]/div[62]/main/div/div/div/div/div[3]/div[2]/div[3]/ul/li/div[2]/div[1]/div['+str(i)+']/button'))
        for i in range(0, len(temp)):
            datesWbt.append([temp[i], temp2[i]])

        modeAllStrikes = driver.find_element_by_xpath('//*[@id="app"]/div[62]/main/div/div/div/div/div[3]/div[2]/div[3]/ul/li/div[2]/div[1]/button[2]')
        

        for date in datesWbt:
            date[1].click()
            Table_NearStrikes = get_table_data(driver, soup)
            modeAllStrikes.click()
            Table_AllStrikes = get_table_data(driver, soup)

            with open(date[0]+'.csv', 'w+', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Near Strikes'])
                writer.writerows(Table_NearStrikes)
                writer.writerows([[], [], ['All Strikes']])
                writer.writerows(Table_AllStrikes)

        input("Enter to exit")
    except Exception as e:
        print(e)
    
main()