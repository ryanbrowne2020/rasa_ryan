from typing import Any, Text, Dict, List, Optional
#
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction
from rasa_sdk import utils
from rasa_sdk.events import SlotSet #needed to set slots from here
from rasa_sdk.events import FollowupAction

#story flow will be :
#story - '002' #this story is about hobby
# user - blah blah 
#action: check_criteria
#action: custom_response_story_002

# of course, be wary of entrenching existing age/gender/cultural stereotypes. 
# don't assume for the user, where possible
# but, want to utilize the results of D3.3

class CheckCriteria(Action):
    def name(self) -> Text:
        return "check_criteria"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

            return []

    #will be filled from digital enabler labels (from initial Rasa form?)
    def getLabelsDE():
        global de_lab_age, de_lab_country, de_lab_hobby, de_lab_sex
        de_lab_country = "Japan"
        de_lab_sex = "male"
        de_lab_age = 72
        de_lab_hobby = "gardening"
        return [de_lab_country, de_lab_sex, de_lab_age, de_lab_hobby]

    getLabelsDE()

    #check age bracket
    def checkAgeBracket():
        global age_bracket
        if de_lab_age < 70:
            age_bracket = 'younger_senior'
        elif 70 <= de_lab_age < 80:
            age_bracket = 'senior'
        elif 80 <= de_lab_age:
            age_bracket = 'older_senior'

    checkAgeBracket()

    #summarize the user profiles into general archetypes
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

class DialogueBranch002(Action):
    def name(self) -> Text:
        return "custom_response_story_002"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

            u = CheckCriteria.getArchetype()

            # during the dialogue, we want to distinguish between male and female, for Japanese younger users
            if u == '1.0':
                # User says hello
                dispatcher.utter_message("Hello sir, let's challenge your friends!")
            elif u == '2.0':
                #user says hello
                dispatcher.utter_message("Hello madam, let's work with your friends!")
            else:
                dispatcher.utter_message("Let's try your hobby today") #fallback 

            #########
            #further depth (if required)
            h = CheckCriteria.getLabelsDE()
            hobby = h[3]

            if u == '1.0' and hobby == 'photography':
                dispatcher.utter_message("Let's go for a walk and take some photos today")
            #we don't care about gender for this one, only age bracket and hobby (for example...)
            elif (u == '2.1' or u == '1.1') and hobby == 'gardening':
                dispatcher.utter_message("Let's work in the garden today")
            elif (u == '2.2' or u == '1.2') and hobby == 'gardening':
                dispatcher.utter_message("If you are feeling fit, let's work in the garden today")

            return []

                