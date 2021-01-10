import discord,os,time,json,random, re
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException

client = discord.Client()
load_dotenv('secrets.env')
discordToken = os.getenv('DISCORD_TOKEN')
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
numberRefDict,nameRefDict = {},{}

@client.event
async def on_ready():
    print('Bot started on account {0.user}'.format(client))
    global numberRefDict,nameRefDict
    with open("numref.json") as f:
        numberRefDict = json.load(f)
    with open("nameref.json") as f:
        nameRefDict = json.load(f)

def webScrape(url):

    wT, aT, wind, wL, aP = False, False, False, False, False
    returnList = ['Could not find','Could not find','Could not find','Could not find','Could not find']

    driver=webdriver.Chrome(chrome_options=chrome_options)
    driver.get(url)
    try:
        sensorTable = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, "//div[@class = 'span12']/table/tbody")))
    except TimeoutException:
        driver.quit()
        return returnList

    for tr in sensorTable.find_elements_by_xpath('.//tr'):
        if tr.find_element_by_xpath('.//td').get_attribute('innerHTML').lower() == "water temperature":
            wT = True
        if tr.find_element_by_xpath('.//td').get_attribute('innerHTML').lower() == "air temperature":
            aT = True
        if tr.find_element_by_xpath('.//td').get_attribute('innerHTML').lower() == "wind":
            wind = True
        if tr.find_element_by_xpath('.//td').get_attribute('innerHTML').lower() == "acoustic wl":
            wL = True
        if tr.find_element_by_xpath('.//td').get_attribute('innerHTML').lower() == "barometric pressure":
            aP = True
    try:     
        if wT:
            wTemp = driver.find_element_by_xpath("//div[@id='wttext']/h1").get_attribute('innerHTML')
            returnList[0] =  wTemp
    except NoSuchElementException:
        pass
    try:
        if aT:
            aTemp = driver.find_element_by_xpath("//div[@id='attext']/h1").get_attribute('innerHTML')
            returnList[1] =  aTemp
    except NoSuchElementException:
        pass
    try:
        if wind:
            windSpeed = driver.find_element_by_xpath("//div[@id='windtext']/h1").get_attribute('innerHTML')
            returnList[2] =  windSpeed
    except NoSuchElementException:
        pass
    try:
        if wL:
            wLevel = driver.find_element_by_xpath("//div[@id='wltext']/h1").get_attribute('innerHTML')
            returnList[3] =  wLevel
    except NoSuchElementException:
        pass
    try:
        if aP:
            airPress = driver.find_element_by_xpath("//div[@id='barotext']/h1").get_attribute('innerHTML')
            returnList[4] =  airPress
    except NoSuchElementException:
        pass

    driver.quit()
    return returnList

@client.event
async def on_message(message):
    global numberRefDict
    if message.author == client.user:
        return

    if message.content.startswith('$temp'):
        startT = time.time()
        params = message.content.split(" ")
        if any(i.isdigit() for i in params[-1]):
            if params[-1] in numberRefDict:
                infoEmbed = discord.Embed(title = numberRefDict[params[-1]].get('name'), color = int(hex(random.randint(0,16777215)),16))
                infoList = webScrape(numberRefDict.get(params[-1]).get('link'))
                infoEmbed.add_field(name = 'Water Temperature', value = infoList[0])
                infoEmbed.add_field(name = 'Air Temperature', value = infoList[1])
                infoEmbed.add_field(name = 'Wind Speed', value = infoList[2])
                infoEmbed.add_field(name = 'Water Level', value = infoList[3])
                infoEmbed.add_field(name = 'Air Pressure', value = infoList[4] + ' millibars')
                await message.channel.send(embed = infoEmbed)
                print(time.time()-startT)
        elif isinstance(params[-1], str):
            for i in numberRefDict:
                if re.search(r"\b" + re.escape(" ".join(params[1:]).lower()) + r"\b", numberRefDict[i].get('name').lower()):
                    infoEmbed = discord.Embed(title = numberRefDict[i].get('name'), color = int(hex(random.randint(0,16777215)),16))
                    infoList = webScrape(numberRefDict[i].get('link'))
                    infoEmbed.add_field(name = 'Water Temperature', value = infoList[0])
                    infoEmbed.add_field(name = 'Air Temperature', value = infoList[1])
                    infoEmbed.add_field(name = 'Wind Speed', value = infoList[2])
                    infoEmbed.add_field(name = 'Water Level', value = infoList[3])
                    infoEmbed.add_field(name = 'Air Pressure', value = infoList[4] + ' millibars')
                    await message.channel.send(embed = infoEmbed)
                    print(time.time()-startT)
                    break
        else:
            await message.channel.send("Weird Params")

    if message.content.startswith('$add'):
        splitMessage = message.content.split(" ")
        if len(splitMessage) == 2:
            await message.channel.send("Weird Params. You need a link and name.")
        else:
            lastNum = list(numberRefDict.keys())[-1]

            y = {str(int(lastNum)+1):{"link" : splitMessage[1], "name" : " ".join(splitMessage[2:])}}

            numberRefDict.update(y)
            print(numberRefDict)

            await message.channel.send("Added " + " ".join(splitMessage[2:]) +"!")

            with open("numref.json", 'w') as f:
                json.dump(numberRefDict, f)
        
    if message.content.startswith('$help'):
        helpEmbed = discord.Embed(title='Commands:', color = int(hex(random.randint(0,16777215)),16))      
        for i in numberRefDict.keys():
            helpEmbed.add_field(name = "Location: " + numberRefDict[i].get('name'), value = "Index: " + str(i))
        await message.channel.send(embed = helpEmbed)

client.run(discordToken)
