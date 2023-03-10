from typing import Any, Text, Dict, List, Optional
#
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction
from rasa_sdk import utils
from rasa_sdk.events import SlotSet #needed to set slots from here
from rasa_sdk.events import FollowupAction

from .action_ryan_time import *
from .con_not_int import * #working. note this is only exercise

from rasa.shared.nlu.training_data.message import Message

from datetime import datetime, date
import time
import math
import sys
import random
import json

# used for presenting in Japanese to older adults @ LL
translatetoJapanese = False

def translate_text(text, des): #this is from EU System code
    """
    param text: the text to be translated
    param des: the target language
    return: the translated text to the target language
    """
    # print(des)
    des = str(des).upper()

    response = requests.post(
        "https://api.deepl.com/v2/translate",
        data={
            "auth_key": "005c8434-eb66-6eb9-0c33-753756ea4b6d",
            "target_lang": des,
            "text": text,
        },
    )
    json_obj = json.loads(response.text)
    try:
        translated = json_obj["translations"][0]["text"]
    except:
        translated = "can not specify the error"
        print("this is the json obj", json_obj)

    return Text(translated)

def translate_utter(utter, language_name): #This is from EU System code
    """
    param utter: the utterance needs to be translated
    param language_name: the target language
    returns: the translated utter in target language
    """
    # global where
    if language_name == "EN":
        text = utter
    else:
        text = translate_text(utter, language_name)

    return text

class SSpeak(): #modified by Ryan for Japanese users         
    def speak(utterance, dispatcher: CollectingDispatcher):
        if translatetoJapanese:
            language_name = "JA"
            utterance = translate_utter(utterance, language_name)
            dispatcher.utter_message(utterance)
        else:
            dispatcher.utter_message(utterance) 

# trackers - send back to DE?
exercise_recommended_today = False 
number_of_videos_viewed = 3
#etc... 

#
class CheckCriteria(Action):
    def name(self) -> Text:
        return "check_criteria"

    def getLabelsDE():
        global de_lab_age, de_lab_country, de_lab_hobby, de_lab_sex
        de_lab_country = "Japan"
        de_lab_sex = "male"
        de_lab_age = 72
        de_lab_hobby = "gardening"
        return [de_lab_country, de_lab_sex, de_lab_age, de_lab_hobby]
    
    def getArchetype():
        if de_lab_country == 'Japan' and de_lab_sex == 'male' and age_bracket == 'younger_senior':
            archetype = '1.0' #younger Japanese male less than 70

        if de_lab_country == 'Japan' and de_lab_sex == 'male' and age_bracket == 'senior':
            archetype = '1.1' #senior Japanese male 70-80

        if de_lab_country == 'Japan' and de_lab_sex == 'male' and age_bracket == 'older_senior':
            archetype = '1.2' #older Japanese male 80+

        if de_lab_country == 'Japan' and de_lab_sex == 'female' and age_bracket == 'younger_senior':
            archetype = '2.0' #younger Japanese female less than 70

        if de_lab_country == 'Japan' and de_lab_sex == 'female' and age_bracket == 'senior':
            archetype = '2.1' #senior Japanese female

        if de_lab_country == 'Japan' and de_lab_sex == 'female' and age_bracket == 'older_senior':
            archetype = '2.2' #older senior Japanese female 80+

        if de_lab_country != 'Japan' and de_lab_sex == 'male' and age_bracket == 'younger_senior':
            archetype = '3.0' #younger European male less than 70

        if de_lab_country != 'Japan' and de_lab_sex == 'male' and age_bracket == 'senior':
            archetype = '3.1' #European male senior 70-80

        if de_lab_country != 'Japan' and de_lab_sex == 'male' and age_bracket == 'older_senior':
            archetype = '3.2' #older European male 80+

        if de_lab_country != 'Japan' and de_lab_sex == 'female' and age_bracket == 'younger_senior':
            archetype = '4.0' #younger European female less than 70

        if de_lab_country != 'Japan' and de_lab_sex == 'female' and age_bracket == 'senior':
            archetype = '4.1' #European female senior 70-80

        if de_lab_country != 'Japan' and de_lab_sex == 'female' and age_bracket == 'older_senior':
            archetype = '4.2' #older European female 80+
        
        return archetype
    
    def checkAgeBracket():
        global age_bracket
        if de_lab_age < 70:
            age_bracket = 'younger_senior'
        elif 70 <= de_lab_age < 80:
            age_bracket = 'senior'
        elif 80 <= de_lab_age:
            age_bracket = 'older_senior'

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

            return []

    getLabelsDE()
    checkAgeBracket()

class DialogueBranchTOP01(Action):
    def name(self) -> Text:
        return "custom_response_story_TOP01"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

            u = CheckCriteria.getArchetype()

            calcStart() #returns program_days

            #example usage...
            if program_days == 0:
                utter = "Welcome to the program! I'll be your coach for smart aging." #add more explanation ...
                SSpeak.speak(utter, dispatcher)

            # during the dialogue, we want to distinguish between male and female, for Japanese younger users
            if u == '1.0': #younger Japanese male less than 70
                utter = "Hello sir, shall we challenge your friends in a game!"
                SSpeak.speak(utter, dispatcher)
            elif u == '2.0': #younger Japanese female less than 70
                utter = "Hello madam, let's work with your friends!"
                SSpeak.speak(utter, dispatcher)
            else: #fallback
                utter = "Let's try your hobby today"
                SSpeak.speak(utter, dispatcher)
            
            #adding further depth (if required)
            h = CheckCriteria.getLabelsDE()
            hobby = h[3]

            if u == '1.0' and hobby == 'photography':
                utter = "Let's go for a walk and take some photos today"
                SSpeak.speak(utter, dispatcher)
            elif (u == '2.1' or u == '1.1') and hobby == 'gardening':
                utter = "Let's work in the garden today"
                SSpeak.speak(utter, dispatcher)
            elif (u == '2.2' or u == '1.2') and hobby == 'gardening':
                utter = "If you are feeling fit, let's work in the garden today"
                SSpeak.speak(utter, dispatcher)

            return []

class DialogueBranchTOP02(Action):
    def name(self) -> Text:
        return "custom_response_story_TOP02"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        #how to do this? level-ii intent?
        utter = "Okay, let me give you a different suggestion"
        SSpeak.speak(utter, dispatcher)
        return []

class DialogueBranchTOP03(Action):
    def name(self) -> Text:
        return "custom_response_story_TOP03"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        #this might be a level-ii intent
        utter = "Okay, I can give you more information ... "
        SSpeak.speak(utter, dispatcher)
        return []
    
class DialogueBranchTOP04(Action):
    def name(self) -> Text:
        return "custom_response_story_TOP04"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        #request specifics 
        nameList = []
        for e in reversed(tracker.events):
            if e["event"] == "action": 
                if e["name"] != "action_listen":
                    if "custom" in e["name"]:
                        nameList.append(e["name"])
        lastUserIntent = nameList[0]

        #example usage
        if lastUserIntent == 'custom_response_story_EX02':
            utter = "Yes I have some specifics for you about exercising outside"
            SSpeak.speak(utter, dispatcher)
        else: #fallback
            utter = "Sorry, I don't have any more specifics about that topic. Feel free to ask me something else!"
            SSpeak.speak(utter, dispatcher)
        return []

class DialogueBranchTOP05(Action):
    def name(self) -> Text:
        return "custom_response_story_TOP05"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        ## entity way: a bit buggy...
        #need to get the domain from entities / check words
        # e.g. I'm not really interested in [brain training](domain_not-interested).
        # entity = tracker.get_slot("domain_non-interest")
        # print(entity)
        # exerciseWords = ['exercise', 'exercising', 'body', 'work out', 'workout']
        # if any(word in entity for word in exerciseWords):
        #     utter = "Okay, you are not interested in exercise"
        #     SSpeak.speak(utter, dispatcher)
        # else: #fallback (domain was mentioned but missed keyword)
        #     utter = "Okay, you are not interested in that"
        #     SSpeak.speak(utter, dispatcher)

        ## python way: it works better ...
        text = (tracker.latest_message)['text']
        exerciseWords = ['exercise', 'exercising', 'body', 'work out', 'workout']
        if any(word in text for word in exerciseWords):
            utter = "Okay, you are not interested in exercise"
            SSpeak.speak(utter, dispatcher)
        else: #fallback (domain was mentioned but missed keyword)
            utter = "Okay, you are not interested in that"
            SSpeak.speak(utter, dispatcher)
        
        return []
    
class DialogueBranchTOP06(Action):
    def name(self) -> Text:
        return "custom_response_story_TOP06"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "Thanks for telling me your plan"
        SSpeak.speak(utter, dispatcher)
        return []


class DialogueBranchTOP08(Action):
    def name(self) -> Text:
        return "custom_response_story_TOP08"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "There's nothing an AI can't do! I guess..."
        SSpeak.speak(utter, dispatcher)
        return []

class DialogueBranchTOP09(Action):
    def name(self) -> Text:
        return "custom_response_story_TOP09"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        dispatcher.utter_message("See you soon. Talk to me anytime")
        utterList = [
            "See you soon. Talk to me anytime", 
            "Take care, talk to me again soon"
        ]
        utter = random.choice(utterList)
        SSpeak.speak(utter, dispatcher)
        
        return []    
    
class DialogueBranchTOP10(Action):
    def name(self) -> Text:
        return "custom_response_story_TOP10"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "So pleased to hear that! Let's stay active today. What activity would you like to do today?"
        SSpeak.speak(utter, dispatcher)
        return []

class DialogueBranchTOP11(Action):
    def name(self) -> Text:
        return "custom_response_story_TOP11"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "I'm sorry to hear that. Some light exercise later might lift your mood?"
        SSpeak.speak(utter, dispatcher)
        return []

class DialogueBranchTOP13(Action):
    def name(self) -> Text:
        return "custom_response_story_TOP13"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "Okay your coaching levels are: exercise - ready; nutrition ... "
        SSpeak.speak(utter, dispatcher)
        
        return []
  
class DialogueBranchTOP14(Action):
    def name(self) -> Text:
        return "custom_response_story_TOP14"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "Sure, let me rephrase that for you."
        SSpeak.speak(utter, dispatcher)
        
        return []
    

### Local topics 

class DialogueBranchLOC01(Action):
    def name(self) -> Text:
        return "custom_response_story_LOC01"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "That's great you are feeling active. Take this chance and go for it!"
        SSpeak.speak(utter, dispatcher)
        
        return []

class DialogueBranchLOC02(Action):
    def name(self) -> Text:
        return "custom_response_story_LOC02"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "Oh that's lovely. Say hello from me."
        SSpeak.speak(utter, dispatcher)
        
        return []
    
class DialogueBranchLOC03(Action):
    def name(self) -> Text:
        return "custom_response_story_LOC03"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "I see, I'll remember about your family members."
        SSpeak.speak(utter, dispatcher)
        
        return []
    
class DialogueBranchLOC04(Action):
    def name(self) -> Text:
        return "custom_response_story_LOC04"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "I hope you can meet up with them soon."
        SSpeak.speak(utter, dispatcher)
        
        return []
    
class DialogueBranchLOC05(Action):
    def name(self) -> Text:
        return "custom_response_story_LOC05"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "If you can spare a moment, think about some good memories you have together."
        SSpeak.speak(utter, dispatcher)
        
        return []

class DialogueBranchLOC06(Action):
    def name(self) -> Text:
        return "custom_response_story_LOC06"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "The recycling is out on Thursdays, and household waste on Fridays"
        SSpeak.speak(utter, dispatcher)
        
        return []

class DialogueBranchLOC07(Action):
    def name(self) -> Text:
        return "custom_response_story_LOC07"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "Okay, you have things to do. Let me know when you are available later"
        SSpeak.speak(utter, dispatcher)
        
        return []
    
class DialogueBranchLOC08(Action):
    def name(self) -> Text:
        return "custom_response_story_LOC08"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "Okay, I can give you some advice on altruism"
        SSpeak.speak(utter, dispatcher)
        
        return []
    
class DialogueBranchLOC09(Action):
    def name(self) -> Text:
        return "custom_response_story_LOC09"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "Okay, I can give you some advice on sustainability"
        SSpeak.speak(utter, dispatcher)
        
        return []

### Cognitive

class DialogueBranchCOG01(Action):
    def name(self) -> Text:
        return "custom_response_story_COG01"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "Okay, I have some brain training games available"
        SSpeak.speak(utter, dispatcher)
        
        return []
    
class DialogueBranchCOG02(Action):
    def name(self) -> Text:
        return "custom_response_story_COG02"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "That's great. Don't forget to wear the 'NeU' headband."
        SSpeak.speak(utter, dispatcher)
        
        return []

class DialogueBranchCOG03(Action):
    def name(self) -> Text:
        return "custom_response_story_COG03"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "Excellent! Your brain deserves a rest. I'll make a note of your score"
        SSpeak.speak(utter, dispatcher)
        
        return []
    
class DialogueBranchCOG04(Action):
    def name(self) -> Text:
        return "custom_response_story_COG04"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "Yes, you can try cognitive training exercises, such as memory games, puzzles, and brain teasers. Additionally, staying physically active, maintaining a healthy diet, and getting enough sleep can also benefit your cognitive health."
        SSpeak.speak(utter, dispatcher)
        
        return []

class DialogueBranchCOG05(Action):
    def name(self) -> Text:
        return "custom_response_story_COG05"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "Keeping mentally and socially active can also benefit your cognitive health. You can try reading books, volunteering, learning a new skill, or connecting with friends and family through regular conversations or activities. Engaging in activities that challenge your brain and keep you mentally and socially active can help maintain cognitive function."
        SSpeak.speak(utter, dispatcher)
        
        return []

class DialogueBranchCOG06(Action):
    def name(self) -> Text:
        return "custom_response_story_COG06"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "While cognitive training can help improve certain cognitive skills, it's not a cure for age-related cognitive decline. However, it can help slow down the process and delay the onset of age-related cognitive issues. It's also important to note that regular physical exercise, healthy diet, and good sleep hygiene can have a positive impact on cognitive health."
        SSpeak.speak(utter, dispatcher)
        
        return []

class DialogueBranchCOG07(Action):
    def name(self) -> Text:
        return "custom_response_story_COG07"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        text = (tracker.latest_message)['text'] #even if user speaks JP, this will refer to the deepL ENG
        focuswords = ['focus', 'focussing', 'focussed', 'attention']
        memorywords = ['memory', 'remember', 'memorization', 'remembering']
        concentratewords = ['concentrate', 'concentration', 'concentrating']
        if any(word in text for word in focuswords):
            utter = "I see. There are ways to improve your focused attention. You can try mindfulness meditation, which involves paying attention to the present moment and your breathing. Regular physical exercise can also improve focus and concentration, as can staying hydrated and getting enough sleep."
            SSpeak.speak(utter, dispatcher)
        elif any(word in text for word in memorywords):
            utter = "I see, you are looking for ways to improve your memory. You can try to "
            SSpeak.speak(utter, dispatcher)
        elif any(word in text for word in concentratewords):
            utterList = ["You can try engaging in activities that require focus, such as reading, working on puzzles, or learning a new skill. You can also try using concentration techniques like mindfulness meditation, which involves paying attention to the present moment and your breathing. Regular practice can help improve your ability to concentrate.",
            "There are several things you can try, such as regular physical exercise, getting enough sleep, and managing stress through activities like mindfulness meditation or deep breathing exercises. Staying hydrated and eating a healthy diet can also have a positive impact on concentration."
            ]
            utter = random.choice(utterList)
            SSpeak.speak(utter, dispatcher)
        else:
            utter = "fallback phrase"
            SSpeak.speak(utter, dispatcher)
        return []

class DialogueBranchCOG08(Action):
    def name(self) -> Text:
        return "custom_response_story_COG08"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "Okay, I can give you some advice on relaxing"
        SSpeak.speak(utter, dispatcher)
        
        return []
    
class DialogueBranchCOG09(Action):
    def name(self) -> Text:
        return "custom_response_story_COG09"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "If you notice changes in your memory, it is best to talk with your doctor"
        SSpeak.speak(utter, dispatcher)
        
        return []
    
class DialogueBranchCOG10(Action):
    def name(self) -> Text:
        return "custom_response_story_COG10"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "Okay, I can tell you about some supplements for brain health"
        SSpeak.speak(utter, dispatcher)
        
        return []


### Social
class DialogueBranchSOC01(Action):
    def name(self) -> Text:
        return "custom_response_story_SOC01"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "That's fantastic you are volunteering. You are really helping others."
        SSpeak.speak(utter, dispatcher)
        
        return []
  
class DialogueBranchSOC02(Action):
    def name(self) -> Text:
        return "custom_response_story_SOC02"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "That's wonderful to hear. I will search the social platform and see what's on."
        SSpeak.speak(utter, dispatcher)
        
        return []

class DialogueBranchSOC03(Action):
    def name(self) -> Text:
        return "custom_response_story_SOC03"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "Thanks for letting me know. I'll remember your hobby."
        SSpeak.speak(utter, dispatcher)
        
        return []
   
class DialogueBranchSOC04(Action):
    def name(self) -> Text:
        return "custom_response_story_SOC04"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "There's a new exhibiton nearby with paintings by Dali"
        SSpeak.speak(utter, dispatcher)
        
        return []
    
class DialogueBranchSOC05(Action):
    def name(self) -> Text:
        return "custom_response_story_SOC05"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "Thanks for letting me know. I'll see what's on then."
        SSpeak.speak(utter, dispatcher)

        #script to check is made recommendation has been filled.
        #if so, then link the free time with the activity
        #or add another story: activities? - recommend, have free time? - i have free time - Action ADD diary
        
        return []
    
class DialogueBranchSOC06(Action):
    def name(self) -> Text:
        return "custom_response_story_SOC06"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "Sure. You might like to connect with Ms Suzuki. She has similar interests to you"
        SSpeak.speak(utter, dispatcher)
        
        return []
    
class DialogueBranchSOC07(Action):
    def name(self) -> Text:
        return "custom_response_story_SOC07"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "Sure, I'll set an alarm for you."
        SSpeak.speak(utter, dispatcher)
        
        return []
    
class DialogueBranchSOC08(Action):
    def name(self) -> Text:
        return "custom_response_story_SOC08"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "Thanks for letting me know. I'll make a note of that. Enjoy your time!"
        SSpeak.speak(utter, dispatcher)
        
        return []
    
class DialogueBranchSOC09(Action):
    def name(self) -> Text:
        return "custom_response_story_SOC09"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "I see. Keeping a regular daily routine is important."
        SSpeak.speak(utter, dispatcher)
        
        return []

class DialogueBranchSOC10(Action):
    def name(self) -> Text:
        return "custom_response_story_SOC10"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "Okay, I can tell you ways to stay in connection"
        SSpeak.speak(utter, dispatcher)
        
        return []
    
class DialogueBranchSOC11(Action):
    def name(self) -> Text:
        return "custom_response_story_SOC11"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "The benefits of social activities are numerous ..."
        SSpeak.speak(utter, dispatcher)
        
        return []
    
class DialogueBranchSOC12(Action):
    def name(self) -> Text:
        return "custom_response_story_SOC12"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "Okay, I can help you to find new hobbies"
        SSpeak.speak(utter, dispatcher)
        
        return []
    
class DialogueBranchSOC13(Action):
    def name(self) -> Text:
        return "custom_response_story_SOC13"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "I understand you are not so interested in social activities"
        SSpeak.speak(utter, dispatcher)
        
        return []

### Spiritual
class DialogueBranchSP01(Action):
    def name(self) -> Text:
        return "custom_response_story_SP01"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
    
        utter = "It's important to make time to reflect. I hope you can do that."
        SSpeak.speak(utter, dispatcher)
        
        return []
    

### Chit--chat

class DialogueBranchCC01(Action):
    def name(self) -> Text:
        return "custom_response_story_CC01"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "Oh, I wish I could talk with animals too. Maybe one day"
        SSpeak.speak(utter, dispatcher)
        
        return []
   
class DialogueBranchCC02(Action):
    def name(self) -> Text:
        return "custom_response_story_CC02"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "That's great. A good drama can stimulate your mind."
        SSpeak.speak(utter, dispatcher)
        
        return []
    
class DialogueBranchCC03(Action):
    def name(self) -> Text:
        return "custom_response_story_CC03"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "That's great, taking a trip can open your mind to new experiences."
        SSpeak.speak(utter, dispatcher)
        
        return []
 
class DialogueBranchCC04(Action):
    def name(self) -> Text:
        return "custom_response_story_CC04"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "Thanks for letting me know. I'll make a note of that."
        SSpeak.speak(utter, dispatcher)
        
        return []
    
### Sleep
class DialogueBranchSL01(Action):
    def name(self) -> Text:
        return "custom_response_story_SL01"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "Glad to hear that. If you are feeling good, let's stay active today."
        SSpeak.speak(utter, dispatcher)
        
        return []
    
class DialogueBranchSL02(Action):
    def name(self) -> Text:
        return "custom_response_story_SL02"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "Sorry to hear that. Let's take it easy today."
        SSpeak.speak(utter, dispatcher)
        
        return []
    
class DialogueBranchSL03(Action):
    def name(self) -> Text:
        return "custom_response_story_SL03"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "It is recommended to sleep 8 hours per night"
        SSpeak.speak(utter, dispatcher)
        
        return []
    
class DialogueBranchSL04(Action):
    def name(self) -> Text:
        return "custom_response_story_SL04"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "From your sleep data, you have been averaging 7.4 hours a night"
        SSpeak.speak(utter, dispatcher)
        
        return []
    
class DialogueBranchSL05(Action):
    def name(self) -> Text:
        return "custom_response_story_SL05"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "To improve your sleep, you can try ..."
        SSpeak.speak(utter, dispatcher)
        
        return []
    
class DialogueBranchSL06(Action):
    def name(self) -> Text:
        return "custom_response_story_SL06"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "As for supplements for sleep ... melatonin ..."
        SSpeak.speak(utter, dispatcher)
        
        return []
    
class DialogueBranchSL07(Action):
    def name(self) -> Text:
        return "custom_response_story_SL07"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "Sleep routine: try to wake up and sleep at the same time"
        SSpeak.speak(utter, dispatcher)
        
        return []
    
class DialogueBranchSL08(Action):
    def name(self) -> Text:
        return "custom_response_story_SL08"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "Relax before bed: avoid blue light (TV, phone)."
        SSpeak.speak(utter, dispatcher)
        
        return []
    
class DialogueBranchSL09(Action):
    def name(self) -> Text:
        return "custom_response_story_SL09"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "Fall asleep: let's do some relaxation strategies together"
        SSpeak.speak(utter, dispatcher)
        
        return []
    
### Exercise 
class DialogueBranchEX01(Action):
    def name(self) -> Text:
        return "custom_response_story_EX01"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "Okay, I'll take a note of your exercise feedback"
        SSpeak.speak(utter, dispatcher)
        
        return []
    
class DialogueBranchEX02(Action):
    def name(self) -> Text:
        return "custom_response_story_EX02"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        currentWeatherSummary('Tokyo')

        if weather_main == 'Clear' or weather_main == 'Clouds':
            utterList = [
                "The weather should be fine! Wear your smartwatch and have a good time.", 
                "Sounds good. It looks clear outside. Don't forget to wear your smartwatch"
            ]
            utter = random.choice(utterList)
            SSpeak.speak(utter, dispatcher)
        elif weather_main == 'Rain' or weather_main == 'Drizzle':
            utterList = [
                "It seems to be raining now, you can decide if you want to go out or not.", 
                "It's raining now. It's up to you to go outside or not!", 
                "It looks like rain, if you decide to go out, bring an umbrella or wear waterproof clothing"
            ]
            utter = random.choice(utterList)
            SSpeak.speak(utter, dispatcher)
        elif weather_main == 'Snow':
            utterList = [
                "It seems to be snowing. Take care, the snow may have caused slippery conditions.", 
                "Snow is falling, take care outside, but also enjoy the white landscape!"
            ]
            utter = random.choice(utterList)
            SSpeak.speak(utter, dispatcher)
        elif weather_main == 'Thunderstorm':
            utterList = [
                "I would advise you not to go outside unless urgent, as there are thunderstorms nearby.", 
                "There seem to be thunderstorms nearby, I would caution against going out right now"
            ]
            utter = random.choice(utterList)
            SSpeak.speak(utter, dispatcher)
        else: #fallback
            utterList = [
                "Okay, take care outside and wear your smartwatch!", 
                "Weather conditions may be changeable. Take care and enjoy your time outside"
            ]
            utter = random.choice(utterList)
            SSpeak.speak(utter, dispatcher)
        
        return []

class DialogueBranchEX03(Action):
    def name(self) -> Text:
        return "custom_response_story_EX03"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "Sure, I can tell you about exercises."
        SSpeak.speak(utter, dispatcher)
        
        return []

class DialogueBranchEX04(Action):
    def name(self) -> Text:
        return "custom_response_story_EX04"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "Right now, you've burned 150 calories. Keep going!"
        SSpeak.speak(utter, dispatcher)
        
        return []

class DialogueBranchEX05(Action):
    def name(self) -> Text:
        return "custom_response_story_EX05"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "You are already quite active I see"
        SSpeak.speak(utter, dispatcher)
        
        return []

class DialogueBranchEX06(Action):
    def name(self) -> Text:
        return "custom_response_story_EX06"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "So, your lifestyle right now is not so active."
        SSpeak.speak(utter, dispatcher)
        
        return []
    
class DialogueBranchEX07(Action):
    def name(self) -> Text:
        return "custom_response_story_EX07"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "It seems like you find ways to incorporate some activity into your daily life"
        SSpeak.speak(utter, dispatcher)
        
        return []

class DialogueBranchEX08(Action):
    def name(self) -> Text:
        return "custom_response_story_EX08"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "The best type of exercise is ..."
        SSpeak.speak(utter, dispatcher)
        
        return []
    
class DialogueBranchEX09(Action):
    def name(self) -> Text:
        return "custom_response_story_EX09"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "You should try to exercise every day if you can, otherwise ..."
        SSpeak.speak(utter, dispatcher)
        
        return []
    
class DialogueBranchEX10(Action):
    def name(self) -> Text:
        return "custom_response_story_EX10"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "If you have joint pains or other issues, I can recommend some videos"
        SSpeak.speak(utter, dispatcher)
        
        return []
    

### Nutrition
class DialogueBranchNU01(Action):
    def name(self) -> Text:
        return "custom_response_story_NU01"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "I can provide you with a mealplan and some recipes, leave it to me!"
        SSpeak.speak(utter, dispatcher)
        
        return []
    
class DialogueBranchNU02(Action):
    def name(self) -> Text:
        return "custom_response_story_NU02"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "Okay, I can tell you some diet advice"
        SSpeak.speak(utter, dispatcher)
        
        return []

class DialogueBranchNU03(Action):
    def name(self) -> Text:
        return "custom_response_story_NU03"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "While it is okay to eat meat for protein, try to reduce how frequently you consume red meat"
        SSpeak.speak(utter, dispatcher)
        
        return []
    
class DialogueBranchNU04(Action):
    def name(self) -> Text:
        return "custom_response_story_NU04"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "Sure, I can teach you a seasonal recipe"
        SSpeak.speak(utter, dispatcher)
        
        return []
    
class DialogueBranchNU05(Action):
    def name(self) -> Text:
        return "custom_response_story_NU05"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "Sure, I can teach you a healthy snack"
        SSpeak.speak(utter, dispatcher)
        
        return []
    
class DialogueBranchNU06(Action):
    def name(self) -> Text:
        return "custom_response_story_NU06"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "Sure, I can teach you how to eat more fruit and veggies"
        SSpeak.speak(utter, dispatcher)
        
        return []
    
class DialogueBranchNU07(Action):
    def name(self) -> Text:
        return "custom_response_story_NU07"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "When dining out, you can ..."
        SSpeak.speak(utter, dispatcher)
        
        return []
    
class DialogueBranchNU08(Action):
    def name(self) -> Text:
        return "custom_response_story_NU08"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "Sure, I can teach you a lot about vitamins and minerals"
        SSpeak.speak(utter, dispatcher)
        
        return []

### General Health
class DialogueBranchGH01(Action):
    def name(self) -> Text:
        return "custom_response_story_GH01"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "I'll work with you to keep your mind and body healthy and active."
        SSpeak.speak(utter, dispatcher)
        
        return []

class DialogueBranchGH02(Action):
    def name(self) -> Text:
        return "custom_response_story_GH02"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "Since you started this program with me, you've lost 2kg"
        SSpeak.speak(utter, dispatcher)
        
        return []

class DialogueBranchGH03(Action):
    def name(self) -> Text:
        return "custom_response_story_GH03"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        ## re: hungover - can use emotional computing to see if they are saying in a fun way "last night was fun", or are feeling bad, etc...
        utter = "I'm really sorry to hear that. Just rest up for now. If you feel any worse, tell me, or call your doctor"
        SSpeak.speak(utter, dispatcher)
        
        return []
    
class DialogueBranchGH04(Action):
    def name(self) -> Text:
        return "custom_response_story_GH04"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "Okay, taking a day off once in a while is good for you"
        SSpeak.speak(utter, dispatcher)
        
        return []

class DialogueBranchGH05(Action):
    def name(self) -> Text:
        return "custom_response_story_GH05"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "Sure. To start, see if you can slowly reduce how many cigarettes you take each day. Replace one cigarette with a tea, or quiet rest time."
        SSpeak.speak(utter, dispatcher)
        
        return []
    
class DialogueBranchGH06(Action):
    def name(self) -> Text:
        return "custom_response_story_GH06"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "Okay, I'll teach you how to maintain a healthy weight"
        SSpeak.speak(utter, dispatcher)
        
        return []

class DialogueBranchGH07(Action):
    def name(self) -> Text:
        return "custom_response_story_GH07"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        utter = "I'll tell you ways to improve your wellbeing"
        SSpeak.speak(utter, dispatcher)
        
        return []

class DialogueBranchGH08(Action):
    def name(self) -> Text:
        return "custom_response_story_GH08"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        #depends very much on previous context
        utter = "I need more context at the moment"
        SSpeak.speak(utter, dispatcher)
        
        return []

contents_interested = [
'...',
'...'
]

contents_practice = [
'...',
'...'
]

i = 0 #simple tracker to vary the 1st and 2nd utterance each day

class GreetRobot(Action):
    def name(self) -> Text:
        return "greet_robot_action"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        #exercise_level = tracker.get_slot("exercise_coaching_level")
        global i

        ##hard-coded for now. will come from Digital Enabler label later...
        exercise_level = "not interested"

        if i == 0:
            utter="I'd like you to take some time, and reflect on what I say next by yourself."
            SSpeak.speak(utter, dispatcher)
            i += 1
        elif i != 0:
            utter = "Here's my coaching comment for now"
            SSpeak.speak(utter, dispatcher)
        if exercise_level == "not interested":
            #script
            text = random.choice(contentList)
        elif exercise_level == "interested":
            #script
            text = random.choice(contents_interested)
        elif exercise_level == "practice":
            #script
            text = random.choice(contents_practice)
        else:
            #backup contents
            text =random.choice(contents)

        # dispatcher.utter_message(response="utter_open", text=text)
        return []