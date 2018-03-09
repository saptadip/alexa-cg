import os
import time
import json
import urllib
import requests

# Variable Declaration
# --------------------
api_base_url1 = os.environ['api_base_url1']
api_base_url2 = os.environ['api_base_url2']


# Main Lambda Fucntion body
# -------------------------
def lambda_handler(event, context):
    if (event["session"]["application"]["applicationId"] !=
            "amzn1.ask.skill.1f929bc5-485e-476e-ada9-73f703e033e6"):
        raise ValueError("Invalid Application ID")
    
    if event["session"]["new"]:
        on_session_started({"requestId": event["request"]["requestId"]}, event["session"])

    if event["request"]["type"] == "LaunchRequest":
        return on_launch(event["request"], event["session"])
    elif event["request"]["type"] == "IntentRequest":
        return on_intent(event["request"], event["session"])
    elif event["request"]["type"] == "SessionEndedRequest":
        return on_session_ended(event["request"], event["session"])

# Lambda Function Declaration End
# -------------------------------



# Supporting Functions Declaration Start
# --------------------------------------

# Function-1: On Session Start
# ----------------------------
def on_session_started(session_started_request, session):
    print "Starting new session."


# Function-2:On Launch
# --------------------
def on_launch(launch_request, session):
    return get_welcome_response()


# Function-3: On Receiving User Intent
# ------------------------------------
def on_intent(intent_request, session):
    intent = intent_request["intent"]
    intent_name = intent_request["intent"]["name"]

    # handle NO intent after the user has been prompted
    if intent_name == 'AMAZON.NoIntent':
        if session.get('session_attributes', {}).get('userPromptedFor_getCryptoPrice'):
            del session['session_attributes']['userPromptedFor_getCryptoPrice']
            return handle_session_end_request()
        elif session.get('session_attributes', {}).get('userPromptedFor_getIcoInfo'):
            del session['session_attributes']['userPromptedFor_getIcoInfo']
            return handle_session_end_request()

    # handle YES intent after the user has been prompted
    if intent_name == "AMAZON.YesIntent":
        if session.get('session_attributes', {}).get('userPromptedFor_getCryptoPrice'):
            del session['session_attributes']['userPromptedFor_getCryptoPrice']
            return get_welcome_response()
        elif session.get('session_attributes', {}).get('userPromptedFor_getIcoInfo'):
            del session['session_attributes']['userPromptedFor_getIcoInfo']
            return get_welcome_response()

    if intent_name == "GetCryptoPrice":
        return get_crypto_price()
    elif intent_name == "GetIcoInfo":
        return get_ico_info()
    elif intent_name == "GetQuickFacts":
        return get_quick_facts()
    elif intent_name == "GetPortfolio":
        return get_portfolio()
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


# Function-4: On Session End
# --------------------------
def on_session_ended(session_ended_request, session):
    print "Ending session."
    # Cleanup goes here...


# Function-5: On Session Close
# ----------------------------
def handle_session_end_request():
    card_title = "Crypto Genie - Thanks"
    speech_output = "Thank you for using the Crypto Genie. Call me anytime you need assistance to explore this amazing world of crypto currencies. I will take you to the moon!! Good bye. "
    should_end_session = True

    return build_response({}, build_speechlet_response(card_title, speech_output, None, should_end_session))


# Function-6: Show Welcome Message
# --------------------------------
def get_welcome_response():
    session_attributes = {}
    card_title = "Crypto Genie"
    speech_output = "Hello! I am Crypto Genie. " \
                    "I can help you to explore the amazing world of crypto currencies. Don't worry, our journey will be full of fun. " \
                    "I will give you five choices. Tell me what you want me to do. Your options are: " \
                    "Choice 1:  Top crypto currency prices. " \
                    "Choice 2:  I C O information. " \
                    "Choice 3:  Social Media facts. " \
                    "Choice 4:  My portfolio. " \
                    "Choice 5:  Latest news. "
    reprompt_text = "Please choose any option between one to five"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


# Function-7: On Getting Crypto Price Intent Request
# --------------------------------------------------
def get_crypto_price():
    session_attributes = {}
    card_title = "Latest Crypto Prices"
    speech_output = "Hmm...I am sorry. I couldn't get the latest price details. " \
                    "Please try again after sometime. "
    reprompt_text = "Hmm...I am sorry. I couldn't get the latest price details. " \
                    "Please try again after sometime. "
    should_end_session = False
    card_title = "Top 10 Crypto Prices "

    r = requests.get(api_base_url1)
    j = json.loads(r.content)
    currency_count = len(j)

    speech_output = " Thank you for your input! Let me search for the latest prices of the top crypto currencies. According to my market analysis, today's top " + str(currency_count) + " currency listings are as follows : "
    for count in range(currency_count):
        cur_name = j[count]['name']
        cur_rank = j[count]['rank']
        cur_price = str(round(float(j[count]['price_usd']), 2))

        speech_output += "Rank " + cur_rank + " : " + cur_name + ". Price : " + cur_price + " dollar " + ". ";

    session_attributes['userPromptedFor_getCryptoPrice'] = True
    speech_output += "So I hope that I successfully fulfilled your request! Let's go to star bucks and grab a coffee. Do you want me to serve you another request? I will do it for free for you!! If you like then say yes, if not, then say no."
    reprompt_text = "I am still waiting for your response. Please say yes if you want to continue. Please say no if you want to exit."

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


# Function-8: On Getting ICO Info Intent Request
# ------------------------//--------------------
def get_ico_info():
    session_attributes = {}
    card_title = "Latest ICOs"
    reprompt_text = ""
    should_end_session = False

    ico_live_req = requests.get(api_base_url2)
    ico_live_json_resp = json.loads(ico_live_req.content)
#    ico_live_count = len(ico_live_json_resp['ico']['live'])
    ico_live_count = 5

    speech_output = " That was a smart choice! Great! Let me search for currently ongoing I C O. Hm, I have found " + str(ico_live_count) + " I C O. Here is the list: "
    for ico_count in range(ico_live_count):
        ico_name = ico_live_json_resp['ico']['live'][ico_count]['name']
        ico_desc = ico_live_json_resp['ico']['live'][ico_count]['description']
        ico_strt = ico_live_json_resp['ico']['live'][ico_count]['start_time']
        ico_end = ico_live_json_resp['ico']['live'][ico_count]['end_time']

        fmtd_ico_strt_dt, fmtd_ico_strt_tm = date_formatter(ico_strt)
        fmtd_ico_end_dt, fmtd_ico_end_tm = date_formatter(ico_end)

        speech_output += "Name: " + ico_name + ". Start date: " + fmtd_ico_strt_dt + ". Time: " + fmtd_ico_strt_tm + ". End date: " + fmtd_ico_end_dt + ". Time: " + fmtd_ico_end_tm + ". Description: " + ico_desc + ". ";

    session_attributes['userPromptedFor_getIcoInfo'] = True
    speech_output += "So that's all I have at the moment. Do you want me to do anything else? Please say yes or no."
    reprompt_text = "Is there something else that I can do for you ? If so, then say yes. If not, then say no. "

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


# Function-9:
# ----------
def get_quick_facts(station_name):
    return {
        "rotterdam central": "rtd",
        "delft": "dt",
        "amsterdam central": "asd",
        "amsterdam airport": "shl",
        "schiphol": "shl",
    }.get(station_name, "unkn")


# Function-10:
# ----------
def get_portfolio(station_name):
    return {
        "rotterdam central": "rtd",
        "delft": "dt",
        "amsterdam central": "asd",
        "amsterdam airport": "shl",
        "schiphol": "shl",
    }.get(station_name, "unkn")


# Function-11:
# -----------
def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        "outputSpeech": {
            "type": "PlainText",
            "text": output
        },
        "card": {
            "type": "Simple",
            "title": title,
            "content": output
        },
        "reprompt": {
            "outputSpeech": {
                "type": "PlainText",
                "text": reprompt_text
            }
        },
        "shouldEndSession": should_end_session
    }


# Function-12:
# -----------
def build_response(session_attributes, speechlet_response):
    return {
        "version": "1.0",
        "sessionAttributes": session_attributes,
        "response": speechlet_response
    }

# Function-13: Date formatting in human readable format
# -----------------------------------------------------
def date_formatter(input_date):
    a = input_date.replace("-", ":")
    b = a.replace(" ", ":")
    c = list(map(int, b.split(":")))
    for i in range(3):
        c.append(0)
    d = tuple(c)
    d = time.mktime(d)
    formatted_date = time.strftime("%A %d %B %Y", time.gmtime(d))
    formatted_time = time.strftime("%r", time.gmtime(d))
    return formatted_date, formatted_time

# Supporting Functions Declaration End
# ------------------------------------

