import os
import time
import json
import urllib
import requests

# Variable Declaration
# --------------------
api_base_url1 = os.environ['api_base_url1']
api_base_url2 = os.environ['api_base_url2']
api_base_url3 = os.environ['api_base_url3']
api_base_url4 = os.environ['api_base_url4']

session_attributes = { 
                        "userPromptedFor_getCryptoPrice" : "",
                        "userPromptedFor_getIcoInfo" : "",
                        "userPromptedFor_getLatestNews" : "",
                        "userPromptedFor_getQuickFacts" : "",
}

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
        return on_intent(event["request"], event["session"], event)
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
def on_intent(intent_request, session, event):
    intent = intent_request["intent"]
    intent_name = intent_request["intent"]["name"]

    # handle NO intent after the user has been prompted
    if intent_name == 'AMAZON.NoIntent':
        if session['attributes']['userPromptedFor_getCryptoPrice']:
            del session['attributes']['userPromptedFor_getCryptoPrice']
            return handle_session_end_request()
        elif session['attributes']['userPromptedFor_getIcoInfo']:
            del session['attributes']['userPromptedFor_getIcoInfo']
            return handle_session_end_request()
        elif session['attributes']['userPromptedFor_getLatestNews']:
            del session['attributes']['userPromptedFor_getLatestNews']
            return handle_session_end_request()
        elif session['attributes']['userPromptedFor_getQuickFacts']:
            del session['attributes']['userPromptedFor_getQuickFacts']
            return handle_session_end_request()
        else:
            return handle_session_end_request()

    # handle YES intent after the user has been prompted
    if intent_name == "AMAZON.YesIntent":
        if session['attributes']['userPromptedFor_getCryptoPrice']:
            del session['attributes']['userPromptedFor_getCryptoPrice']
            return get_welcome_response()
        elif session['attributes']['userPromptedFor_getIcoInfo']:
            del session['attributes']['userPromptedFor_getIcoInfo']
            return get_welcome_response()
        elif session['attributes']['userPromptedFor_getLatestNews']:
            del session['attributes']['userPromptedFor_getLatestNews']
            return get_welcome_response()
        elif session['attributes']['userPromptedFor_getQuickFacts']:
            del session['attributes']['userPromptedFor_getQuickFacts']
            return get_welcome_response()
        else:
            return handle_session_end_request()

    if intent_name == "GetCryptoPrice":
        return get_crypto_price()
    elif intent_name == "GetIcoInfo":
        return get_ico_info()
    elif intent_name == "GetQuickFacts":
        return get_quick_facts(intent, event)
    elif intent_name == "GetPortfolio":
        return get_portfolio()
    elif intent_name == "GetLatestNews":
        return get_latest_news()
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        return handle_session_end_request()


# Function-4: On Session End
# --------------------------
def on_session_ended(session_ended_request, session):
    print "Ending session."
    # Cleanup goes here...


# Function-5: On Session Close
# ----------------------------
def handle_session_end_request():
    card_title = "Crypto Genie - Thanks"
    speech_output = "Thank you for using Crypto Genie. Call me anytime you need assistance to explore this amazing world of crypto currencies. I will take you to the moon!! Good bye. "
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
                    "Choice 2:  Ongoing I C O. " \
                    "Choice 3:  Social Media facts. " \
                    "Choice 4:  My portfolio. " \
                    "Choice 5:  Crypto headlines. "
    reprompt_text = "Please choose any option between one to five"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


# Function-7: On Getting Crypto Price Intent Request
# --------------------------------------------------
def get_crypto_price():
    card_title = "Top 10 Crypto Prices"
    should_end_session = False
    speech_output = "Hmm...I am sorry. I couldn't get the latest price details. " \
                    "Please try again after sometime. "
    reprompt_text = "Hmm...I am sorry. I couldn't get the latest price details. " \
                    "Please try again after sometime. "

    r = requests.get(api_base_url1)
    j = json.loads(r.content)
    currency_count = len(j)

    speech_output = " Thank you for your input! Let me search for the latest prices of the top crypto currencies. According to my market analysis, today's top " + str(currency_count) + " currency listings are as follows : "
    for count in range(currency_count):
        cur_name = j[count]['name']
        cur_rank = j[count]['rank']
        cur_price = str(round(float(j[count]['price_usd']), 2))

        speech_output += "Rank " + cur_rank + " : " + cur_name + ". Price : " + cur_price + " dollar " + ". ";

    session_attributes["userPromptedFor_getCryptoPrice"] = "true"
    speech_output += "So I hope that I successfully fulfilled your request! Let's go to star bucks and grab a coffee. Do you want me to serve you another request? I will do it free for you!! If you like then say yes, if not, then say no."
    reprompt_text = "I am still waiting for your response. Please say yes if you want to continue. Please say no if you want to exit."

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


# Function-8: On Getting ICO Info Intent Request
# ----------------------------------------------
def get_ico_info():
    card_title = "CG - Latest ICOs"
    should_end_session = False
    speech_output = "Hmm...I am sorry. I couldn't get the I C O details. " \
                    "Please try again after sometime. "
    reprompt_text = "Hmm...I am sorry. I couldn't get the I C O details. " \
                    "Please try again after sometime. "

    ico_live_req = requests.get(api_base_url2)
    ico_live_json_resp = json.loads(ico_live_req.content)
#   ico_live_count = len(ico_live_json_resp['ico']['live'])
    ico_live_count = 5

    speech_output = " That was a smart choice! Great! Let me search for currently ongoing I C O. Hm, I have found " + str(ico_live_count) + " I C O. Here is the list: "
    for ico_count in range(ico_live_count):
        ico_name = ico_live_json_resp['ico']['live'][ico_count]['name']
        ico_desc = ico_live_json_resp['ico']['live'][ico_count]['description']
        ico_strt = ico_live_json_resp['ico']['live'][ico_count]['start_time']
        ico_end = ico_live_json_resp['ico']['live'][ico_count]['end_time']

        fmtd_ico_strt_dt, fmtd_ico_strt_tm = date_formatter(ico_strt)
        fmtd_ico_end_dt, fmtd_ico_end_tm = date_formatter(ico_end)

        speech_output += "I C O name: " + ico_name + ". Start date: " + fmtd_ico_strt_dt + ". Time: " + fmtd_ico_strt_tm + ". End date: " + fmtd_ico_end_dt + ". Time: " + fmtd_ico_end_tm + ". Description: " + ico_desc + ". ";

    session_attributes["userPromptedFor_getIcoInfo"] = "true"
    speech_output += "So that's all I have at the moment. Do you want me to do anything else? Please say yes or no."
    reprompt_text = "Is there something else that I can do for you ? If so, then say yes. If not, then say no. To exit, please say stop or cancel"

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


# Function-9 On Getting Social Media Facts Intent Request:
# --------------------------------------------------------
def get_quick_facts(intent, event):
    dialog_state = event['request']['dialogState']
    if dialog_state in ("STARTED", "IN_PROGRESS"):
        return continue_dialog()
    elif dialog_state == "COMPLETED":
        return collect_social_media_info(intent)
    else:
        return handle_session_end_request()


def continue_dialog():
    message = {}
    message['should_end_session'] = False
    message['directives'] = [{'type': 'Dialog.Delegate'}]
    return build_dialogue_response(message)


def build_dialogue_response(message, session_attributes={}):
    response = {}
    response['version'] = '1.0'
    response['sessionAttributes'] = session_attributes
    response['response'] = message
    return response


def collect_social_media_info(intent):
    card_title = "CG - Social Media Facts"
    speech_output = "Sorry, I do not know the currency you just said. Please try again."
    reprompt_text = "If you are not sure, try some well know currency. Like: Bitcoin."
    should_end_session = False

    if "Currency" in intent["slots"]:
       try:
          currency_name = intent["slots"]["Currency"]["value"]
       except KeyError:
          return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
       
       currency_code = get_currency_code(currency_name.lower())

       if (currency_code != "unkn"):
            card_title = "CG - Social Media Facts " + currency_name.title()
            r = requests.get(api_base_url3 + currency_code)
            j = json.loads(r.content)

          # twitter Account Stats
          #----------------------
            try:
                twtr_acc_name = j['Data']['Twitter']['name']
            except KeyError:
                twtr_acc_name = "not available"
            try:
                twtr_acc_link = j['Data']['Twitter']['link']
            except KeyError:
                twtr_acc_link = "not available"
            try:
                twtr_tweet_count = j['Data']['Twitter']['statuses']
            except KeyError:
                twtr_tweet_count = "not available"
            try:
                twtr_like_count = j['Data']['Twitter']['favourites']
            except KeyError:
                twtr_like_count = "not available"
            try:
                twtr_follower_count = j['Data']['Twitter']['followers']
            except KeyError:
                twtr_follower_count = "not available"

          # reddit Account Stats
          #---------------------
            try:
                rdit_acc_name = j['Data']['Reddit']['name']
            except KeyError:
                rdit_acc_name = "not available"
            try:
                rdit_acc_link = j['Data']['Reddit']['link']
            except KeyError:
                rdit_acc_link = "not available"
            try:
                rdit_actv_user_count = j['Data']['Reddit']['active_users']
            except KeyError:
                rdit_actv_user_count = "not available"
            try:
                rdit_subscrb_count = j['Data']['Reddit']['subscribers']
            except KeyError:
                rdit_subscrb_count = "not available"
            try:
                rdit_posts_per_hour = j['Data']['Reddit']['posts_per_hour']
            except KeyError:
                rdit_posts_per_hour = "not available"
            try:
                rdit_comnts_per_hour = j['Data']['Reddit']['comments_per_hour']
            except KeyError:
                rdit_comnts_per_hour = "not available"
            try:
                rdit_posts_per_day = j['Data']['Reddit']['posts_per_day']
            except KeyError:
                rdit_posts_per_day = "not available"
            try:
                rdit_comnts_per_day = j['Data']['Reddit']['comments_per_day']
            except KeyError:
                rdit_comnts_per_day = "not available"

          # facebook account stats
          #-----------------------
            try:
                fb_like_count = j['Data']['Facebook']['likes']
            except KeyError:
                fb_like_count = "not available"
            try:
                fb_talking_count = j['Data']['Facebook']['talking_about']
            except KeyError:
                fb_talking_count = "not available"
            try:
                fb_link = j['Data']['Facebook']['link']
            except KeyError:
                fb_link = "not available"


            session_attributes["userPromptedFor_getQuickFacts"] = "true"
            speech_output = " I collected all the latest social media related activities on " + currency_name + " and created a personalized report card for you. So are you ready? Here we go: " \
                            "Twitter account name is: " + twtr_acc_name + ". Number of followers on Twitter is: " + twtr_follower_count + ". Total tweet count is: " + twtr_tweet_count + ". Total number of tweets liked by the users is: " + twtr_like_count + ". " \
                            "Reddit account name is: " + rdit_acc_name + ". Number of active users on Reddit is: " + rdit_actv_user_count + ". Total subscriber count on reddit is: " + rdit_subscrb_count + ". Number of posts per hour is: " + rdit_posts_per_hour + ". Number of comments per hour is: " + rdit_comnts_per_hour + ". Number of posts per day is: " + rdit_posts_per_day + ". Number of comments per day is: " + rdit_comnts_per_day + ". " \
                            "On Facebook number of likes received on the homepage is: " + fb_like_count + ". Number of people talking about " + currency_name + " on facebook is: " + fb_talking_count + ". " \
                            "So that is all I can find on social media about " + currency_name + ". I hope my report was useful for you.  Do you want me to do anything else for you? Please say yes or no."
            reprompt_text = "Hmm I did not get that. Do you want me to continue? Please say yes or no. To exit, please say stop or cancel"

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))



def get_latest_news():
    card_title = "CG - Crypto News Headlines"
    speech_output = "Hmm...I am sorry. I couldn't get the latest news. " \
                    "Please try again after sometime. "
    reprompt_text = "Hmm...I am sorry. I couldn't get the latest news. " \
                    "Please try again after sometime. "
    should_end_session = False

    day_hrs_in_epoch = 86400
    cur_time_in_epoch = int(time.time())
    last_time_in_epoch = cur_time_in_epoch - day_hrs_in_epoch
    r = requests.get(api_base_url4 + str(cur_time_in_epoch))
    j = json.loads(r.content)
    total_news_count = len(j)

    speech_output = "Here is the top crypto related headlines from last 24 hours. "
    for count in range(total_news_count):
        publish_time_in_epoch = int(j[count]["published_on"])
        if publish_time_in_epoch >= last_time_in_epoch:
            news_headlines = j[count]["title"].encode('utf-8')
            speech_output += news_headlines + ". "
        else:
            break

    session_attributes["userPromptedFor_getLatestNews"] = "true"
    speech_output += "That's all for now. Thank you for using crypto genie news service. Do you want me to serve you another request? I will do it free for you!! If you like then say yes, if not, then say no.";
    reprompt_text = "I am still waiting for your response. Please say yes if you want to continue. Please say no if you want to exit."

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


# Function-10:
# ----------
def get_portfolio():
    card_title = "CG - My Portfolio"
    speech_output = "I am still learning how to get your portfolio status. Please check again after few days. "
    reprompt_text = "Thank you for showing interest. Please check again after few days. "
    should_end_session = True

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))




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


# Function-14: Get Currency Code
# ------------------------------
def get_currency_code(currency_name):
    return {
        "bitcoin": "1182",
        "ethereum": "7605",
        "litecoin": "3808",
    }.get(currency_name, "unkn")



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


# Supporting Functions Declaration End
# ------------------------------------
