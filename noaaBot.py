import discord,os,time,json,random
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

client = discord.Client()
load_dotenv('secrets.env')
discordToken = os.getenv('DISCORD_TOKEN')
chrome_options = webdriver.ChromeOptions()
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
    print(url)
    driver=webdriver.Chrome(chrome_options=chrome_options)
    driver.get(url)
    try:
        wTempElement = WebDriverWait(driver,15).until(EC.presence_of_element_located((By.XPATH, "//div[@id='wttext']/h1")))
        wTemp = driver.find_element_by_xpath("//div[@id='wttext']/h1").get_attribute('innerHTML')
        driver.quit()
        return wTemp
    except TimeoutException:
        driver.quit()
        return "Couldn't find watertemp!"

@client.event
async def on_message(message):
    global numberRefDict
    if message.author == client.user:
        return

    if message.content.startswith('$temp'):
        startT = time.time()
        params = message.content.split(" ")
        if any(i.isdigit() for i in params[-1]):
            print(numberRefDict)
            if params[-1] in numberRefDict:
                await message.channel.send("Water Temperature for " + numberRefDict[params[-1]].get('name') + ": " + webScrape(numberRefDict.get(params[-1]).get('link')))
                print(time.time()-startT)


            # if int(params[-1]) == 1:
            #     await message.channel.send(webScrape(numberRefDict.get(params[-1])))
            #     print(time.time()-startT)
            # elif int(params[-1]) == 2:
            #     await message.channel.send(webScrape(numberRefDict.get(params[-1])))
        # elif isinstance(params[-1], str):
        #     print("name")
        #     print(params[-1])
        #     if params[-1].lower() == "Washington Channel".lower():
        #         await message.channel.send(webScrape(nameRefDict.get(params[-1])))
        #         print(time.time()-startT)
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

            await message.channel.send("Added!")

            with open("numref.json", 'w') as f:
                json.dump(numberRefDict, f)
        
        # y = {int(lastNum)+1:message.content.split(" ")[-1]}

        # print(message.content.split(" ")[-1])

        # numberRefDict.update(y)

        # await message.channel.send("Added!")

        # with open("numref.json", 'w') as f:
        #     json.dump(numberRefDict,f)

    if message.content.startswith('$help'):
        helpEmbed = discord.Embed(title='Commands:', color = int(hex(random.randint(0,16777215)),16))      
        for i in numberRefDict.keys():
            helpEmbed.add_field(name = "Location: " + numberRefDict[i].get('name'), value = "Index: " + str(i))
        await message.channel.send(embed = helpEmbed)



        # if message.content[1:].lower() == "temp":
        #     startTime = time.time()
        #     driver=webdriver.Chrome(chrome_options=chrome_options)
        #     driver.get("https://tidesandcurrents.noaa.gov/stationhome.html?id=8594900")

        #     driver.quit()
        #     print(time.time()-startTime)
        #     await message.channel.send(wTemp)


        # await message.channel.send('Hello!')

client.run(discordToken)
