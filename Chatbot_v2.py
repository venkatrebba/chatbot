from textblob import TextBlob
#from attributegetter import *
from generatengrams import ngrammatch
from Contexts import *
import json
from Intents import *
import random
import os
import re
import string
import querycsv3 as querycsv

def ResetAction():
    return IntentComplete()

def GetContext(contextName, oldContext):
    if(contextName == ""):
        return oldContext
    if(contextName == "GetCuisine"):
        return GetCuisine()
    if(contextName == "GetRestaurantLocation"):
        return GetRestaurantLocation()
    if(contextName == "GetCostrange"):
        return GetCostrange()
    if(contextName == "GetCabLocation"):
        return GetCabLocation()
    if(contextName == "GetLuggage"):
        return GetLuggage()
    if(contextName == "GetPassengers"):
        return GetPassengers()

def check_actions(current_intent, attributes, context):
    '''This function performs the action for the intent
    as mentioned in the intent config file'''
    '''Performs actions pertaining to current intent
    for action in current_intent.actions:
        if action.contexts_satisfied(active_contexts):
            return perform_action()
    '''
    print(current_intent.action)
    if(current_intent.action == 'resetcontext'):
        context = ResetAction()
        return None, context

    elif(current_intent.action == 'BookRestaurant'):
        tableName = 'db_restaurant'
        fileName = os.getcwd() + "/" + tableName + ".csv"

        print('inside restaurent action... checking order for following params')

        queryString = "select * from " + tableName + " where "
        for key,value in attributes.items():
            print(key + ":\t" + str(value))
            queryString += " TRIM(LOWER(`" + key + "`)) "+ " = \"" + str(value).lower() + "\" and "
        queryString = queryString[:-4]
        #print("query :" + queryString)

        resultList, columnList = querycsv.qcsv([fileName], None, None, None, queryString)

        print("==========================================================")
        if(len(resultList) == 0):
            print('No results found.!!')
        else:
            print(columnList)
            print("------------------------------------------------------")
            print(random.choice(resultList))
            print("=======================================================")
    elif(current_intent.action == 'BookCab'):
        tableName = 'db_cabbooking'
        fileName = os.getcwd() + "/" + tableName + ".csv"
        print('inside cabboking action')
        queryString = "select * from " + tableName + " where "
        for key, value in attributes.items():
            print(key + ":\t" + str(value))
            queryString += " TRIM(LOWER(`" + key + "`)) "+ " = \"" + str(value).lower() + "\" and "
        queryString = queryString[:-4]
        #print("query :" + queryString)
        resultList, columnList = querycsv.qcsv([fileName], None, None, None, queryString)

        print("==========================================================")
        if (len(resultList) == 0):
            print('No results found.!!')
        else:
            print(columnList)
            print("------------------------------------------------------")
            print(random.choice(resultList))
            print("=======================================================")

    else:
        print('Given intent is not found ..!!, intent = ' + current_intent.action)
    context = IntentComplete()
    return None, context

def check_required_params(current_intent, attributes, context):
    '''Collects attributes pertaining to the current intent'''
    
    #if(current_intent.name == 'Reset'):
    #    return None, IntentComplete()
    if(len(current_intent.params) == 0 or current_intent.params == None):
        if(current_intent.name == 'Reset'):
            return None, ResetContext()
        return None, context
    for para in current_intent.params:
        if para.required == 'True':
            if para.name not in attributes:
                #Example of where the context is born, implemented in
                #Contexts.py
                context = GetContext(para.context, context)
                #returning a random prompt frmo available choices.
                #print('context switch: ' + context.name)
                return random.choice(para.prompts), context
    return None, context


def input_processor(user_input, context, attributes, intent):
    '''Spellcheck and entity extraction functions go here'''
    print('before spell check : input =' + user_input)
    uinput = TextBlob(user_input).correct().string
    print('after spell check : input =' + uinput)
    #update the attributes, abstract over the entities in user input
    attributes, cleaned_input = getattributes(user_input, context, attributes)
    
    return attributes, cleaned_input

def loadIntent(path, intent):
    with open(path) as fil:
        dat = json.load(fil)
        intent = dat[intent]
        return Intent(intent['intentname'],intent['Parameters'], intent['actions'])

def intentIdentifier(clean_input, context,current_intent):
    clean_input = clean_input.lower()

    if(current_intent != 'Reset' and current_intent != None):
        return current_intent

    #Scoring Algorithm, can be changed.
    scores = ngrammatch(clean_input)
    
    #choosing here the intent with the highest score
    scores = sorted_by_second = sorted(scores, key=lambda tup: tup[1])
    # print clean_input
    #print 'scores', scores
    newIntent = loadIntent('params/newparams.cfg',scores[-1][0])
    if(newIntent.name == 'Reset'):
       return newIntent
    if(current_intent == None):
        return newIntent
    else:
        #If current intent is not none, stick with the ongoing intent
        return current_intent

def getattributes(uinput,context,attributes):
    '''This function marks the entities in user input, and updates
    the attributes dictionary'''
    #Can use context to context specific attribute fetching
    if context.name.startswith('IntentComplete'):
        return attributes, uinput
    #if(context.name.startswith('IntentComplete')):
    else:
        #Code can be optimised here, loading the same files each time
        #suboptimal
        files = os.listdir('./entities/')
        entities = {}
        for fil in files:
            lines = open('./entities/' + fil).readlines()
            for i, line in enumerate(lines):
                lines[i] = line[:-1]
            entities[fil[:-4]] = '|'.join(lines)

        numberList = entities['passengers'].split('|')
        # Extract entity and update it in attributes dict
        for entity in entities:

            if(context.placeholder != '' and  context.placeholder[1:] !=  entity):
                continue

            if (entity == 'passengers' and context.placeholder == '' or context.name == 'GetPassengers'):
                rangeMatched = False
                mat = re.search("\d+[ a-zA-z-]+\d+", uinput)
                if (mat != None):
                    rangeMatched = True
                    print(mat.group())
                    numList = re.findall('\d', mat.group())
                    minV = min(numList)
                    maxV = max(numList)
                    if((minV in numberList) and (maxV in numberList)):
                        attributes[entity] = str(random.randint(int(minV),int(maxV)))
                        uinput = re.sub(mat.string, r'$passengers', uinput, flags=re.IGNORECASE)
                elif(not rangeMatched):
                    for si in uinput.split(" "):
                        if (si in numberList):
                            attributes[entity] = si
            else:
                for i in entities[entity].split('|'):
                    if i.lower() in uinput.lower():
                        attributes[entity] = i
        '''     
        if (context.name == 'GetPassengers'):
            numberList = entities['passengers'].split('|')
            for si in uinput.split(" "):
                if(si in numberList ):
                        attributes['passengers'] = si
        '''
        for entity in entities:
            uinput = re.sub(entities[entity], r'$' + entity, uinput, flags=re.IGNORECASE)

        '''
        if (context.name != 'GetPassengers'):
            for entity in entities:
                uinput = re.sub(entities[entity], r'$' + entity, uinput, flags=re.IGNORECASE)
        else:
            passengerNumbers = entities['passengers'].replace('|', '$|') + '$'
        '''

        return attributes, uinput

def convertData(current_intent,attributes):
    if(current_intent == 'Reset' or current_intent == None or (not attributes)):
        return attributes

    textNumDict = {"one":1,"two":2,"three":3,"four":4,"five":5,"six":6,"seven":7}
    params = current_intent.params
    for par in params:
        if par.name in attributes.keys():
            data_value = str(attributes[par.name])
            if(par.datatype == 'Int' and (not data_value.isdigit())):
                attributes[par.name] = textNumDict[data_value]
    return attributes


class Session:
    def __init__(self, attributes=None, active_contexts=[FirstGreeting(), IntentComplete()]):
        
        '''Initialise a default session'''
        
        #Active contexts not used yet, can use it to have multiple contexts
        self.active_contexts = active_contexts
        
        #Contexts are flags which control dialogue flow, see Contexts.py
        self.context = FirstGreeting()
        
        #Intent tracks the current state of dialogue
        #self.current_intent = First_Greeting()
        self.current_intent = None
        
        #attributes hold the information collected over the conversation
        self.attributes = {}
        
    def update_contexts(self):
        '''Not used yet, but is intended to maintain active contexts'''

        '''
        for context in self.active_contexts:
            if context.active:
                context.decrease_lifespan()
        '''

    def reply(self, user_input):
        '''Generate response to user input'''
        
        self.attributes, clean_input = input_processor(user_input, self.context, self.attributes, self.current_intent)
        
        self.current_intent = intentIdentifier(clean_input, self.context, self.current_intent)

        self.attributes = convertData(self.current_intent,self.attributes)

        prompt, self.context = check_required_params(self.current_intent, self.attributes, self.context)


        #prompt being None means all parameters satisfied, perform the intent
        #action
        if prompt is None:
            if self.context.name != 'IntentComplete':
                prompt, self.context = check_actions(self.current_intent, self.attributes, self.context)

        #Resets the state after the Intent is complete
        if self.context.name == 'IntentComplete':
            self.attributes = {}
            self.context = FirstGreeting()
            self.current_intent = None
        
        return prompt

session = Session()

print('BOT: Hi! How may I assist you?')

#for restaurant
#data: location-where to eat
#       cost range: cheap, affordable, expensive
#       cuisine: north-indian, continental, all-egg, bengali
while True:
    
    inp = input('User: ')
    #re.sub("",r'$'+entity,uinput,flags=re.IGNORECASE)
    botReply = session.reply(inp)
    if(botReply != None):
        print('BOT:', botReply)
    if(session.current_intent == None):
        print('\nBOT: Can I help you with anything else?')