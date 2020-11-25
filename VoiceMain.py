import requests
import json
import pyttsx3
import speech_recognition as sr
import re
import threading
import time


API_KEY="taM7kcpmBKNL"
TOKEN="ttTUBfKCdzJT"
RUN_TOKEN="tpyrhiKbZc8Q"



class Data:
    def __init__(self,api_key,project_token):
        self.api_key=api_key
        self.project_token=project_token
        self.params={
            "api_key":self.api_key
        }
        self.data=self.getData()
    def getData(self):
        
        response=requests.get(f'https://www.parsehub.com/api/v2/projects/{self.project_token}/last_ready_run/data', params=self.params)
        data=json.loads(response.text)
        return data

    def get_total_cases(self):
        data=self.data['total']
        for x in data:
            if x['name']=="Coronavirus Cases:":
                return x['value']


    def get_total_deaths(self):
        data=self.data['total']
        for x in data:
            if x['name']=="Deaths:":
                return x['value']

        return "0"

    def get_country_data(self,country):
        data=self.data["countries"]
        for info in data:
            if info["name"].lower()==country.lower():
                return info

        return "0"

    def get_all_countries(self):
        countries=[]
        for country in self.data['countries']:
            countries.append(country['name'].lower())

        return countries     

    def update_data(self):
        response=requests.post(f'https://www.parsehub.com/api/v2/projects/{self.project_token}/run', params=self.params)
        
        def poll():
            time.sleep(0.1)
            old_data=self.data
            while True:
                new_data=self.getData()
                if new_data !=old_data:
                    self.data=new_data
                    print("data updated!!")
                    break
                time.sleep(5)

        t=threading.Thread(target=poll)
        t.start()



def speak(text):
    engine=pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def get_audio():
    r=sr.Recognizer()
    with sr.Microphone() as source:
        audio=r.listen(source)
        said=""

        try:
            said=r.recognize_google(audio)
        except Exception as e:
            print("Exception:", str(e))

    return said.lower()            



def main():
    data=Data(API_KEY,TOKEN)
    print("Program is working")
    end="stop"
    update="update"
    countryList=data.get_all_countries()
    total_patterns ={
        re.compile("[\w\s]+ total [\w\s]+ cases"):data.get_total_cases,
        re.compile("[\w\s]+ total cases"):data.get_total_cases,
        re.compile("[\w\s]+ total [\w\s]+ deaths"):data.get_total_deaths,
        re.compile("[\w\s]+ total deaths"):data.get_total_deaths,
    }
    country_patterns={
         re.compile("[\w\s]+ cases [\w\s]+"): lambda country:data.get_country_data(country)['total_cases'],
          re.compile("[\w\s]+ deaths [\w\s]+"): lambda country:data.get_country_data(country)['total_deaths']
    }


    while True:
        print("Listening for your speech..")
        word=get_audio()
        print(word)
        result=None

        for pattern,funct in country_patterns.items():
            if pattern.match(word):
                words=set(word.split(" "))
                for country in countryList:
                    if country in words:
                        result=funct(country)
                        break


        for pattern,funct in total_patterns.items():
            if pattern.match(word):
                result=funct()
                break

        if word==update:
            result="Data is being updated"
            data.update_data()
                

        if result:
            print(result)
            speak(result)
        if word.find(end)!=-1:
            print("exit")
            break

main()        