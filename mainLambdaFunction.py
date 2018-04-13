import os
import time
import json
import boto3
import urllib
import string
import decimal
import requests
import datetime
from boto3.dynamodb.conditions import Key, Attr

# Variable Declaration
# --------------------
session_attributes = { 
                        "userPromptedFor_getCryptoPrice" : "",
                        "userPromptedFor_getIcoInfo" : "",
                        "userPromptedFor_getLatestNews" : "",
                        "userPromptedFor_getQuickFacts" : "",
                        "userPromptedFor_getPortfolioStatus" : "",
                        "userPromptedFor_getAnyCryptoPrice" : "",
                    }

# Main Lambda Fucntion body
# -------------------------
def lambda_handler(event, context):
    if (event["session"]["application"]["applicationId"] !=
            "amzn1.ask.skill.1f929bc5-485e-476e-ada9-73f703e033e6"):
        raise ValueError("Invalid Application ID")

    try:
        access_token = event['context']['System']['user']['accessToken']
    except:
        access_token = None
    
    if event["session"]["new"]:
        on_session_started({"requestId": event["request"]["requestId"]}, event["session"])

    if event["request"]["type"] == "LaunchRequest":
        return on_launch(event["request"], event["session"], access_token)
    elif event["request"]["type"] == "IntentRequest":
        return on_intent(event, access_token)
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
def on_launch(launch_request, session, access_token):
    return get_welcome_response(access_token)


# Function-3: On Receiving User Intent
# ------------------------------------
def on_intent(event, access_token):
    intent = event["request"]["intent"]
    intent_name = event["request"]["intent"]["name"]
    session = event["session"]

    # handle NO intent after the user has been prompted
    if intent_name == 'AMAZON.NoIntent':
        if session['attributes']['userPromptedFor_getCryptoPrice']:
            del session['attributes']['userPromptedFor_getCryptoPrice']
            return handle_session_end_request()
        elif session['attributes']['userPromptedFor_getIcoInfo']:
            del session['attributes']['userPromptedFor_getIcoInfo']
            return handle_session_end_request()
        elif session['attributes']['userPromptedFor_getAnyCryptoPrice']:
            del session['attributes']['userPromptedFor_getAnyCryptoPrice']
            return handle_session_end_request()
        elif session['attributes']['userPromptedFor_getLatestNews']:
            del session['attributes']['userPromptedFor_getLatestNews']
            return handle_session_end_request()
        elif session['attributes']['userPromptedFor_getQuickFacts']:
            del session['attributes']['userPromptedFor_getQuickFacts']
            return handle_session_end_request()
        elif session['attributes']['userPromptedFor_getPortfolioStatus']:
            del session['attributes']['userPromptedFor_getPortfolioStatus']
            return handle_session_end_request()
        else:
            return handle_session_end_request()

    # handle YES intent after the user has been prompted
    if intent_name == "AMAZON.YesIntent":
        if session['attributes']['userPromptedFor_getCryptoPrice']:
            del session['attributes']['userPromptedFor_getCryptoPrice']
            return get_welcome_response(access_token)
        elif session['attributes']['userPromptedFor_getIcoInfo']:
            del session['attributes']['userPromptedFor_getIcoInfo']
            return get_welcome_response(access_token)
        elif session['attributes']['userPromptedFor_getAnyCryptoPrice']:
            del session['attributes']['userPromptedFor_getAnyCryptoPrice']
            return get_welcome_response(access_token)
        elif session['attributes']['userPromptedFor_getLatestNews']:
            del session['attributes']['userPromptedFor_getLatestNews']
            return get_welcome_response(access_token)
        elif session['attributes']['userPromptedFor_getQuickFacts']:
            del session['attributes']['userPromptedFor_getQuickFacts']
            return get_welcome_response(access_token)
        elif session['attributes']['userPromptedFor_getPortfolioStatus']:
            del session['attributes']['userPromptedFor_getPortfolioStatus']
            return get_welcome_response(access_token)
        else:
            return handle_session_end_request()

    if intent_name == "GetCryptoPrice":
        return get_crypto_price()
    elif intent_name == "GetIcoInfo":
        return get_ico_info()
    elif intent_name == "GetAnyCryptoPrice":
        return get_any_crypto_price(intent, event)
    elif intent_name == "GetQuickFacts":
        return get_quick_facts(intent, event)
    elif intent_name == "GetPortfolio":
        return get_portfolio(intent, event, access_token)
    elif intent_name == "AddCoin":
        return add_to_portolio(intent, event, access_token)
    elif intent_name == "DeleteCoin":
        return del_frm_portolio(intent, event, access_token)
    elif intent_name == "GetLatestNews":
        return get_latest_news()
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response(access_token)
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
    speech_output = "Thank you for using Crypto Genie. Good bye!! "
    should_end_session = True

    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))



# Function-6: Show Welcome Message
# --------------------------------
def get_welcome_response(access_token):
    session_attributes = {}
    card_title = "Crypto Genie - Welcome"
    if access_token is None:
        speech_output = "Your user details are not available at this time.  Please complete account linking via the Alexa app and try again later."
        reprompt_text = ""
        should_end_session = True
    else:
        user_details = get_user_info(access_token)
        if user_details is None:
            speech_output = "There was a problem getting your user details."
            reprompt_text = ""
            should_end_session = True
        else:
            speech_output = "Hello " + user_details['name'].split(" ")[0] + "! My name is Crypto Genie. " \
                            "Please choose any one option from the below list. Your options are: " \
                            "Choice 1:  Top crypto currency prices . " \
                            "Choice 2:  Check price of any coin . " \
                            "Choice 3:  Ongoing I C O list . " \
                            "Choice 4:  Social Media facts . " \
                            "Choice 5:  Crypto headlines . " \
                            "Choice 6:  Add coin to portfolio . " \
                            "Choice 7:  Remove coin from portfolio . " \
                            "Choice 8:  Get portfolio status . " \
                            "You can say stop anytime to stop me from processing your request. Or say help to allow me to guide you. "
            reprompt_text = "Please choose any option between one to eight"
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

    r = requests.get(os.environ['api_base_url1'])
    j = json.loads(r.content)
    currency_count = len(j)

    speech_output = " Thank you for your input! According to the market report, today's top " + str(currency_count) + " currency listings are as follows : "
    for count in range(currency_count):
        cur_name = j[count]['name']
        cur_rank = j[count]['rank']
        cur_price = str(round(float(j[count]['price_usd']), 2))

        speech_output += "Rank " + cur_rank + " : " + cur_name + ". Price : " + cur_price + " dollar " + ". ";

    session_attributes["userPromptedFor_getCryptoPrice"] = "true"
    speech_output += "  So that is all for now. Do you want me to serve you another request? " \
                     " If you like then say yes. If you want me to stop, then say no."
    reprompt_text = "I am still waiting for your response. Please say yes if you want to continue. Please say no if " \
                    "you want to exit."

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

    ico_live_req = requests.get(os.environ['api_base_url2'])
    ico_live_json_resp = json.loads(ico_live_req.content)
#   ico_live_count = len(ico_live_json_resp['ico']['live'])
    ico_live_count = 5

    speech_output = " That was a smart choice! Here is the top " + str(ico_live_count) + " I C O that are currently on going. "
    for ico_count in range(ico_live_count):
        ico_name = ico_live_json_resp['ico']['live'][ico_count]['name']
        ico_desc = ico_live_json_resp['ico']['live'][ico_count]['description']
        ico_strt = ico_live_json_resp['ico']['live'][ico_count]['start_time']
        ico_end = ico_live_json_resp['ico']['live'][ico_count]['end_time']

        fmtd_ico_strt_dt, fmtd_ico_strt_tm = date_formatter(ico_strt)
        fmtd_ico_end_dt, fmtd_ico_end_tm = date_formatter(ico_end)

        speech_output += "I C O name: " + ico_name + ". Start date: " + fmtd_ico_strt_dt + ". Start time: " + fmtd_ico_strt_tm + \
                         ". End date: " + fmtd_ico_end_dt + ". End time: " + fmtd_ico_end_tm + ". Description: " + ico_desc + ".          ";

    session_attributes["userPromptedFor_getIcoInfo"] = "true"
    speech_output += "So that's all I have at the moment. Do you want me to do anything else? " \
                    "Please say yes to continue. Or say no to exit."
    reprompt_text = "Is there something else that I can do for you ? If so, then say yes. " \
                    "If not, then say no. To exit, please say stop or cancel"

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
    speech_output = "Sorry, I can not recognize the currency you just said. Please try again. Say yes to continue. Or say no to exit. "
    reprompt_text = "If you are not sure, try some well know currency. Like: Bitcoin. "
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
            r = requests.get(os.environ['api_base_url3'] + currency_code)
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
            speech_output = " OK. Getting the latest social media related activities on " + str(currency_name) + ". Report is ready. Here we go: " \
                            "Twitter account statistics. Account name: " + str(twtr_acc_name) + ". Number of followers: " + str(twtr_follower_count) + \
                            ". Total tweet count: " + str(twtr_tweet_count) + ". Total number of tweets liked by the users: " + twtr_like_count + ". " \
                            "Reddit account statistics. Account name: " + str(rdit_acc_name) + ". Number of active users: " + str(rdit_actv_user_count) + \
                            ". Total number of subscribers: " + str(rdit_subscrb_count) + ". Number of posts per hour: " + str(rdit_posts_per_hour) + \
                            ". Number of comments per hour: " + str(rdit_comnts_per_hour) + ". Number of posts per day: " + str(rdit_posts_per_day) + \
                            ". Number of comments per day: " + str(rdit_comnts_per_day) + ". Facebook account statistics. Number of likes: " + \
                            str(fb_like_count) + ". Number of people talking about " + str(currency_name) + " on facebook is: " + str(fb_talking_count) + ". " \
                            "So that is all I can find on social media about " + str(currency_name) + ". I hope my report was useful for you. " \
                            "Do you want me to do anything else for you? Please say yes or no."
            reprompt_text = "Hmm I did not get that. Do you want me to continue? Please say yes or no. To exit, please say stop or cancel"

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))



def get_any_crypto_price(intent, event):
    dialog_state = event['request']['dialogState']
    if dialog_state in ("STARTED", "IN_PROGRESS"):
        return continue_dialog()
    elif dialog_state == "COMPLETED":
        return ger_cur_price(intent)
    else:
        return handle_session_end_request()



def ger_cur_price(intent):
    card_title = "CG - Coin Price Check"
    speech_output = "Sorry. I can not recognize the currency you are looking for. I hope you know that I can only understand currency symbol. " \
                    "Like if you want to know the price of bitcoin, please say BTC, without any space . Thank you for your understanding. Good bye!!"
    should_end_session = False

    if "Currency" in intent["slots"]:
        try:
            user_cur = (intent["slots"]["Currency"]["value"]).replace(" ","").upper()
        except KeyError:
            return build_response(session_attributes, build_speechlet_response(
                card_title, speech_output, reprompt_text, should_end_session))


    base_cur = 'USD'
    url = os.environ['api_base_url6']
    url = string.replace(url, 'VAR1', user_cur)
    url = string.replace(url, 'VAR2', base_cur)
    r = requests.get(url)
    j = json.loads(r.content)

    if base_cur in j:
        usd_price = str(j['USD'])
        session_attributes["userPromptedFor_getAnyCryptoPrice"] = "true"
        reprompt_text = "I am still waiting for your response. "
        speech_output = "The current price of " + str(user_cur) + " is " + usd_price + " U S D. " \
                        "Do you want me to do anything else for you? Please say yes to continue. Or say no to exit."
        return build_response(session_attributes, build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session))
    else:
        should_end_session = True
        reprompt_text = ""
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
    r = requests.get(os.environ['api_base_url4'] + str(cur_time_in_epoch))
    j = json.loads(r.content)
    total_news_count = len(j)

    speech_output = "Here is the top crypto related headlines from last 24 hours. "
    for count in range(total_news_count):
        publish_time_in_epoch = int(j[count]["published_on"])
        if publish_time_in_epoch >= last_time_in_epoch:
            news_headlines = j[count]["title"].encode('utf-8')
            speech_output += news_headlines + ".             "
        else:
            break

    session_attributes["userPromptedFor_getLatestNews"] = "true"
    speech_output += "That's all for now. Thank you for using crypto genie news service. Do you want me to serve you another request? " \
                     "I will do it for free!! If you like then say yes, if not, then say no.";
    reprompt_text = "I am still waiting for your response. Please say yes if you want to continue. Please say no if you want to exit."

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


# Function-10:
# ----------
def get_portfolio(intent, event, access_token):
    if access_token is not None:
        user_details = get_user_info(access_token)
        if user_details is None:
            session_attributes = {}
            card_title = "CG - Goodbye!"
            speech_output = "There was a problem getting your user details."
            reprompt_text = ""
            should_end_session = True
            return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))
        else:
            dynamodb = boto3.resource('dynamodb')
            tablename = 'cg-user-details'
            table = dynamodb.Table(tablename)
            user_id = user_details['user_id'].split(".")[0] + user_details['user_id'].split(".")[2]
            user_name = check_user_account(table, user_id)

            if user_name:
                user_key = (user_id, user_name)
                return get_portfolio_details(intent, event, table, user_key)
            else:
                dialog_state = event['request']['dialogState']
                if dialog_state in ("STARTED", "IN_PROGRESS"):
                    return continue_dialog()
                elif dialog_state == "COMPLETED":
                    return create_user_account(intent, event, table, user_details)
                else:
                    return handle_session_end_request()
    else:
        session_attributes = {}
        card_title = "CG - Goodbye!"
        speech_output = "Your user details are not available at this time.  Please complete account linking via " \
                        "the Alexa app and try again later."
        reprompt_text = ""
        should_end_session = True
        return build_response(session_attributes, build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session))



def check_user_account(table, user_id):
    response = table.query(KeyConditionExpression=Key('id').eq(user_id))
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        items = response['Items']
        if not items:
            return False
        else:
            return items[0]['name']
    else:
        speech_output = "I am unable to check your account. Please try again after some time."
        reprompt_text = ""
        should_end_session = True
        return build_response(session_attributes, build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session))



def create_user_account(intent, event, table, user_details):
    speech_output = "There was a problem getting your user details."
    reprompt_text = ""
    should_end_session = True
    card_title = "CG - Goodbye!!"

    portfolio_user_name = user_details['name']
    portfolio_user_email = user_details['email']

    if "Currency" in intent["slots"]:
        try:
            portfolio_currency = (intent["slots"]["Currency"]["value"]).replace(" ","").upper()
        except KeyError:
            return build_response(session_attributes, build_speechlet_response(
                card_title, speech_output, reprompt_text, should_end_session))

    if "Quantity" in intent["slots"]:
        try:
            portfolio_quantity_whole = int(intent["slots"]["Quantity"]["value"])
        except KeyError:
            return build_response(session_attributes, build_speechlet_response(
                card_title, speech_output, reprompt_text, should_end_session))

    if "FractionalQuantity" in intent["slots"]:
        try:
            portfolio_quantity_fraction = int(intent["slots"]["FractionalQuantity"]["value"])
        except KeyError:
            return build_response(session_attributes, build_speechlet_response(
                card_title, speech_output, reprompt_text, should_end_session))

    if "Price" in intent["slots"]:
        try:
            portfolio_price_sat = float(intent["slots"]["Price"]["value"])
        except KeyError:
            return build_response(session_attributes, build_speechlet_response(
                card_title, speech_output, reprompt_text, should_end_session))

    if portfolio_quantity_fraction not in [1,10,100,1000,10000,100000]:
        speech_output = "Sorry. You have entered invalid fractional quantity. It must be any one of the following values " \
                        "one, ten, one hundred, one thousand, ten thousand or one hundred thousand . Please try again. Good bye!!"
        return build_response(session_attributes, build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session))

    portfolio_quantity = decimal.Decimal(str(round((float(portfolio_quantity_whole) / float(portfolio_quantity_fraction)),2)))

    base_cur = 'USD'
    url = os.environ['api_base_url6']
    url = string.replace(url, 'VAR1', portfolio_currency)
    url = string.replace(url, 'VAR2', base_cur)
    r = requests.get(url)
    j = json.loads(r.content)

    if base_cur not in j:
        speech_output = "Sorry. I can not find the currency you want to add. I hope you know that I can only understand currency symbol. " \
                        "Like if you want to add bitcoin to your portfolio, please say BTC, without any space . Thank you for your understanding. Good bye!!"
        return build_response(session_attributes, build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session))

    btc_to_sat = float(100000000)
    btc_to_usd = float(str(get_btc_price()))
    portfolio_price_btc = portfolio_price_sat / btc_to_sat
    portfolio_price_usd = decimal.Decimal(str(round((portfolio_price_btc * btc_to_usd),2)))
    portfolio_price = portfolio_price_usd

    input_userid = user_details['user_id'].split(".")[0] + user_details['user_id'].split(".")[2]
    input_name = portfolio_user_name
    input_email = portfolio_user_email
    input_account_type = 1
    input_account_status = "A"
    input_portfolio = [{"cur": portfolio_currency , "qty": portfolio_quantity, "prc": portfolio_price}]
    input_portfolio_access_time = str(datetime.datetime.now()).split(".")[0]
    input_request_serve_count = 0


    response = table.put_item(
                Item={
                'id': input_userid,
                'name': input_name,
                'email': input_email,
                'type': input_account_type,
                'status': input_account_status,
                'portfolio' : input_portfolio,
                'lastSeen': input_portfolio_access_time,
                'totReqCt' : input_request_serve_count,
            }
        )

    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        speech_output = "Hurray !! " + user_details['name'].split(" ")[0] + ", your portfolio has been " \
                        "created successfully! To check your portfolio value, please launch the skill and choose option " \
                        "eight. "
        return build_response(session_attributes, build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session))
    else:
        speech_output = "I am unable to create your portfolio. Sorry for the inconvenience, but looks like there is a remote connectivity problem. " \
                        "So please try again after some time."
        reprompt_text = ""
        return build_response(session_attributes, build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session))




def get_portfolio_details(intent, event, table, user_key):
    card_title = "CG - My Portfolio Status"
    speech_output = "I am unable to get your portfolio status. Please try again later. "
    reprompt_text = "Thank you for your interest. Please check again after few days. "
    should_end_session = False

    portfolio_val_old = 0
    portfolio_val_new = 0
    user_id = user_key[0]
    user_name = user_key[1]

    response = table.get_item(Key={'id' : user_id,'name' : user_name})
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        items = response['Item']
        portfolio = items['portfolio']
        req_count = int(items['totReqCt']) + 1
        access_time = str(datetime.datetime.now()).split(".")[0]

        table.update_item(
            Key={
                'id': user_id,
                'name': user_name
            },
            UpdateExpression='SET totReqCt = :val1, lastSeen = :val2',
            ExpressionAttributeValues={
                ':val1': req_count,
                ':val2': access_time
            }
        )
    else:
        speech_output = "I am unable to get your portfolio status. Please try again later. "
        reprompt_text = ""
        should_end_session = True
        return build_response(session_attributes, build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session))


    if not portfolio:
        speech_output = "Hmm. " + str(user_name.split(" ")[0]) + ", your portfolio is empty. Please add some coins to your portfolio and try again. Goodbye!! "
        reprompt_text = ""
        should_end_session = True
        card_title = "CG - Goodbye!!"
        return build_response(session_attributes, build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session))
    else:
        for x in portfolio:
            cur = x['cur'].encode('UTF8')
            qty = decimal.Decimal(x['qty'])
            buy_prc = decimal.Decimal(x['prc'])
            portfolio_val_old += buy_prc * qty
            
            base_cur = 'USD'
            url = os.environ['api_base_url6']
            url = string.replace(url, 'VAR1', cur)
            url = string.replace(url, 'VAR2', base_cur)
            r = requests.get(url)
            j = json.loads(r.content)
            cur_prc = decimal.Decimal(str(j['USD']))
            portfolio_val_new += cur_prc * qty

    portfolio_prcnt_change = ((portfolio_val_new - portfolio_val_old) / portfolio_val_old) * 100
    portfolio_prcnt_change_abs = round(decimal.Decimal(abs(portfolio_prcnt_change)),2)

    if portfolio_prcnt_change > 0:
        portfolio_status = "profit"
        portfolio_msg = "I am so happy "
    else:
        portfolio_status = "loss"
        portfolio_msg = "Hmm. I am sorry "


    session_attributes["userPromptedFor_getPortfolioStatus"] = "true"
    speech_output = user_name.split(" ")[0] + ", your current portfolio valuation is. " + str(round((float(portfolio_val_new)),2)) + " dollars. " \
                    + portfolio_msg + "to say, that your portfolio is showing " + str(portfolio_prcnt_change_abs) + " percent " \
                    + str(portfolio_status) + ". Do you want me to do anything else for you? Please say yes to continue. Or say no to exit."
    reprompt_text = "I am still waiting for your response. Please say yes if you want to continue. Please say no if you want to exit."

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


# Function to add coin to portfolio
#----------------------------------

def add_to_portolio(intent, event, access_token):
    if access_token is not None:
        user_details = get_user_info(access_token)
        if user_details is None:
            session_attributes = {}
            card_title = "CG - Goodbye!"
            speech_output = "There was a problem getting your user details."
            reprompt_text = ""
            should_end_session = True
            return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))
        else:
            dynamodb = boto3.resource('dynamodb')
            tablename = 'cg-user-details'
            table = dynamodb.Table(tablename)
            user_id = user_details['user_id'].split(".")[0] + user_details['user_id'].split(".")[2]
            user_name = check_user_account(table, user_id)

            if user_name:
                user_key = (user_id, user_name)
                dialog_state = event['request']['dialogState']
                if dialog_state in ("STARTED", "IN_PROGRESS"):
                    return continue_dialog()
                elif dialog_state == "COMPLETED":
                    return add_coin_to_portfolio(intent, event, table, user_key)
                else:
                    return handle_session_end_request()
            else:
                dialog_state = event['request']['dialogState']
                if dialog_state in ("STARTED", "IN_PROGRESS"):
                    return continue_dialog()
                elif dialog_state == "COMPLETED":
                    return create_user_account(intent, event, table, user_details)
                else:
                    return handle_session_end_request()
    else:
        card_title = "CG - Goodbye!"
        speech_output = "Your user details are not available at this time.  Please complete account linking via " \
                        "the Alexa app and try again later."
        reprompt_text = ""
        should_end_session = True
        return build_response(session_attributes, build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session))



def add_coin_to_portfolio(intent, event, table, user_key):
    user_id = user_key[0]
    user_name = user_key[1]
    item_match_index = 0
    cur_exist = False
    x = int(intent["slots"]["Quantity"]["value"])
    y = int(intent["slots"]["FractionalQuantity"]["value"])

    if y not in [1,10,100,1000,10000,100000]:
        speech_output = "Sorry. You have entered invalid fractional quantity. It must be any one of the following values. " \
                        "One, ten, one hundred, one thousand, ten thousand or one hundred thousand . Please try again. Good bye!!"
        card_title = "CG - Goodbye!"
        session_attributes = {}
        should_end_session = True
        reprompt_text = ""
        return build_response(session_attributes, build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session))

    base_cur = 'USD'
    portfolio_currency = (intent["slots"]["Currency"]["value"]).replace(" ","").upper()
    url = os.environ['api_base_url6']
    url = string.replace(url, 'VAR1', portfolio_currency)
    url = string.replace(url, 'VAR2', base_cur)
    r = requests.get(url)
    j = json.loads(r.content)

    if base_cur not in j:
        speech_output = "Sorry. I can not find the currency you want to add. I hope you know that I can only understand currency symbol. " \
                        "Like if you want to add bitcoin to your portfolio, please say BTC, without any space . Thank you for your understanding. Good bye!!"
        reprompt_text = ""
        should_end_session = True
        card_title = "CG - Goodbye!!"
        session_attributes = {}
        return build_response(session_attributes, build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session))


    response = table.get_item(Key={'id' : user_id,'name' : user_name})
    if (response['ResponseMetadata']['HTTPStatusCode'] == 200 and "Currency" in intent["slots"]):
        items = response['Item']
        portfolio = items['portfolio']
        item_count = len(portfolio)
        for count in range(item_count):
            portfolio_item = portfolio[count]
            if portfolio_currency == portfolio_item.get('cur').encode('UTF8'):
                cur_exist = True
                item_match_index = count
                break

        if cur_exist:
            matched_item = portfolio[item_match_index]
            old_qty = decimal.Decimal(matched_item.get('qty'))
            new_qty = decimal.Decimal(str(round((float(x) / float(y)),2)))
            total_qty = old_qty + new_qty
            old_prc = decimal.Decimal(matched_item.get('prc'))

            portfolio_price_sat = float(intent["slots"]["Price"]["value"])
            btc_to_sat = float(100000000)
            btc_to_usd = float(str(get_btc_price()))
            portfolio_price_btc = portfolio_price_sat / btc_to_sat
            portfolio_price_usd = decimal.Decimal(str(round((portfolio_price_btc * btc_to_usd),2)))
            new_prc = portfolio_price_usd

            total_prc = (old_prc * old_qty) + (new_prc * new_qty)
            prc = decimal.Decimal(str(round((total_prc / total_qty),2)))
            matched_item['qty'] = total_qty
            matched_item['prc'] = prc
            portfolio[item_match_index] = matched_item
        else:
            portfolio_price_sat = float(intent["slots"]["Price"]["value"])
            btc_to_sat = float(100000000)
            btc_to_usd = float(str(get_btc_price()))
            portfolio_price_btc = portfolio_price_sat / btc_to_sat
            portfolio_price_usd = decimal.Decimal(str(round((portfolio_price_btc * btc_to_usd),2)))
            new_prc = portfolio_price_usd
            new_qty = decimal.Decimal(str(round((float(x) / float(y)),2)))

            new_cur = {
                        "cur": str(portfolio_currency),
                        "qty": new_qty,
                        "prc": new_prc
                    }
            portfolio.append(new_cur)


        req_count = int(items['totReqCt']) + 1
        access_time = str(datetime.datetime.now()).split(".")[0]

        table.update_item(
            Key={'id': user_id,'name': user_name},
            UpdateExpression='SET totReqCt = :val1, lastSeen = :val2, portfolio = :val3',
            ExpressionAttributeValues={':val1': req_count,':val2': access_time,':val3': portfolio}
        )

        speech_output = "I have successfully added " + str(new_qty) + " quantity of " \
                        + str(intent["slots"]["Currency"]["value"]) + " bought at the rate of " + \
                        str(new_prc) + " dollar. Thank you for using crypto genie. Good bye! "
        reprompt_text = ""
        card_title = "CG - Goodbye!"
        should_end_session = True
        session_attributes = {}
        return build_response(session_attributes, build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session))
    else:
        speech_output = "I am unable to get your portfolio status. Please try again later. "
        reprompt_text = ""
        should_end_session = True
        session_attributes = {}
        return build_response(session_attributes, build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session))



# Function to Delete coin from portfolio
# --------------------------------------

def del_frm_portolio(intent, event, access_token):
    if access_token is not None:
        user_details = get_user_info(access_token)
        if user_details is None:
            session_attributes = {}
            card_title = "CG - Goodbye!"
            speech_output = "There was a problem getting your user details."
            reprompt_text = ""
            should_end_session = True
            return build_response(session_attributes, build_speechlet_response(
                card_title, speech_output, reprompt_text, should_end_session))
        else:
            dynamodb = boto3.resource('dynamodb')
            tablename = 'cg-user-details'
            table = dynamodb.Table(tablename)
            user_id = user_details['user_id'].split(".")[0] + user_details['user_id'].split(".")[2]
            user_name = check_user_account(table, user_id)

            if user_name:
                user_key = (user_id, user_name)
                dialog_state = event['request']['dialogState']
                if dialog_state in ("STARTED", "IN_PROGRESS"):
                    return continue_dialog()
                elif dialog_state == "COMPLETED":
                    return del_coin_frm_portfolio(intent, event, table, user_key)
                else:
                    return handle_session_end_request()
            else:
                card_title = "CG - Goodbye!"
                session_attributes = {}
                speech_output = "You have not created your portfolio. Please relaunch the skill and add some coins to your portfolio by selecting option six. Good bye!"
                reprompt_text = ""
                should_end_session = True
                return build_response(session_attributes, build_speechlet_response(
                    card_title, speech_output, reprompt_text, should_end_session))
                
    else:
        card_title = "CG - Goodbye!"
        speech_output = "Your user details are not available at this time.  Please complete account linking via " \
                        "the Alexa app and try again later."
        reprompt_text = ""
        should_end_session = True
        session_attributes = {}
        return build_response(session_attributes, build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session))



def del_coin_frm_portfolio(intent, event, table, user_key):
    user_id = user_key[0]
    user_name = user_key[1]
    item_match_index = 0
    cur_exist = False
    x = int(intent["slots"]["Quantity"]["value"])
    y = int(intent["slots"]["FractionalQuantity"]["value"])

    if y not in [1,10,100,1000,10000,100000]:
        speech_output = "Sorry. You have entered invalid fractional quantity. It must be any one of the following values. " \
                        "One, ten, one hundred, one thousand, ten thousand or one hundred thousand . Please try again. Good bye!!"
        card_title = "CG - Goodbye!"
        session_attributes = {}
        should_end_session = True
        reprompt_text = ""
        return build_response(session_attributes, build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session))


    base_cur = 'USD'
    portfolio_currency = (intent["slots"]["Currency"]["value"]).replace(" ","").upper()
    url = os.environ['api_base_url6']
    url = string.replace(url, 'VAR1', portfolio_currency)
    url = string.replace(url, 'VAR2', base_cur)
    r = requests.get(url)
    j = json.loads(r.content)

    if base_cur not in j:
        speech_output = "Sorry. I can not find the currency you want to add. I hope you know that I can only understand currency symbol. " \
                        "Like if you want to add bitcoin to your portfolio, please say BTC, without any space . Thank you for your understanding. Good bye!!"
        reprompt_text = ""
        should_end_session = True
        card_title = "CG - Goodbye!!"
        session_attributes = {}
        return build_response(session_attributes, build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session))


    response = table.get_item(Key={'id' : user_id,'name' : user_name})
    if (response['ResponseMetadata']['HTTPStatusCode'] == 200 and "Currency" in intent["slots"]):
        items = response['Item']
        portfolio = items['portfolio']
        item_count = len(portfolio)
        for count in range(item_count):
            portfolio_item = portfolio[count]
            if portfolio_currency == portfolio_item.get('cur').encode('UTF8'):
                cur_exist = True
                item_match_index = count
                break

        if cur_exist:
            matched_item = portfolio[item_match_index]
            old_qty = decimal.Decimal(matched_item.get('qty'))
            new_qty = decimal.Decimal(str(round((float(x) / float(y)),2)))
            if old_qty > new_qty:
                total_qty = old_qty - new_qty
                matched_item['qty'] = total_qty
                portfolio[item_match_index] = matched_item
            elif old_qty == new_qty:
                del portfolio[item_match_index]
                req_count = int(items['totReqCt']) + 1
                access_time = str(datetime.datetime.now()).split(".")[0]

                table.update_item(
                    Key={'id': user_id,'name': user_name},
                    UpdateExpression='SET totReqCt = :val1, lastSeen = :val2, portfolio = :val3',
                    ExpressionAttributeValues={':val1': req_count,':val2': access_time,':val3': portfolio}
                )

                card_title = "CG - Goodbye!"
                speech_output = str(intent["slots"]["Currency"]["value"]) + " has been removed from your portfolio successfully. " \
                                "To get the latest status of your portfolio, please re-launch the skill and choose option eight. Good bye!!"
                reprompt_text = ""
                session_attributes = {}
                should_end_session = True
                return build_response(session_attributes, build_speechlet_response(
                    card_title, speech_output, reprompt_text, should_end_session))
            else:
                card_title = "CG - Goodbye!"
                speech_output = "You do not have " + str(new_qty) + " " + str(portfolio_currency) + " in your portfolio. "\
                                "So I can not fulfill your request. Good bye!!"
                reprompt_text = ""
                should_end_session = True
                session_attributes = {}
                return build_response(session_attributes, build_speechlet_response(
                    card_title, speech_output, reprompt_text, should_end_session))
        else:
            card_title = "CG - Goodbye!"
            speech_output = "The requested coin does not exist in your portfolio. So I am sorry that I can not fulfill your request. Good bye!!"
            reprompt_text = ""
            should_end_session = True
            session_attributes = {}
            return build_response(session_attributes, build_speechlet_response(
                card_title, speech_output, reprompt_text, should_end_session))


        req_count = int(items['totReqCt']) + 1
        access_time = str(datetime.datetime.now()).split(".")[0]

        table.update_item(
            Key={'id': user_id,'name': user_name},
            UpdateExpression='SET totReqCt = :val1, lastSeen = :val2, portfolio = :val3',
            ExpressionAttributeValues={':val1': req_count,':val2': access_time,':val3': portfolio}
        )

        new_qty = decimal.Decimal(str(round((float(x) / float(y)),2)))
        speech_output = "I have successfully removed " + str(new_qty) + " quantity of " \
                        + str(intent["slots"]["Currency"]["value"]) + " from your portfolio. To get the latest status " \
                        "of your portfolio, please re-launch the skill and choose option eight." + \
                        " Thank you for using crypto genie. Good bye! "
        reprompt_text = ""
        card_title = "CG - Goodbye!"
        should_end_session = True
        session_attributes = {}
        return build_response(session_attributes, build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session))
    else:
        speech_output = "I am unable to get your portfolio status from the database. looks like there is remote connectivity problem. Please try again after some time. "
        reprompt_text = ""
        should_end_session = True
        session_attributes = {}
        return build_response(session_attributes, build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session))



def get_btc_price():
    url = os.environ['api_base_url6']
    url = string.replace(url, 'VAR1', 'BTC')
    url = string.replace(url, 'VAR2', 'USD')
    r = requests.get(url)
    j = json.loads(r.content)

    if 'USD' not in j:
        reprompt_text = ""
        should_end_session = True
        card_title = "CG - Goodbye!!"
        session_attributes = {}
        speech_output = "Sorry. I can not connect to the server to check the latest price. Please try again after sometime. Goodbye!!"
        return build_response(session_attributes, build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session))
    else:
        return j['USD']



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



def get_user_info(access_token):
    amazonProfileURL = 'https://api.amazon.com/user/profile?access_token='
    r = requests.get(url=amazonProfileURL+access_token)
    if r.status_code == 200:
        return r.json()
    else:
        return False



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
