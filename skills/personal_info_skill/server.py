#!/usr/bin/env python

import logging
import time
import re

from flask import Flask, request, jsonify
from os import getenv
import sentry_sdk

from common.constants import CAN_NOT_CONTINUE, MUST_CONTINUE
from common.weather import ASK_WEATHER_SKILL_FOR_HOMELAND_PHRASE
from common.utils import get_entities, get_named_locations, get_named_persons, is_no, is_yes


sentry_sdk.init(getenv('SENTRY_DSN'))

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.route("/respond", methods=['POST'])
def respond():
    st_time = time.time()
    dialogs_batch = request.json["dialogs"]
    confidences = []
    responses = []
    human_attributes = []
    bot_attributes = []
    attributes = []

    for dialog in dialogs_batch:
        human_attr, bot_attr = {}, {}
        response, confidence, attr = how_do_you_know_my_info(dialog, which_info="name")
        if confidence == 0.0:
            response, confidence, attr = how_do_you_know_my_info(dialog, which_info="location")
        if confidence == 0.0:
            response, confidence, attr = how_do_you_know_my_info(dialog, which_info="homeland")

        if confidence == 0.0:
            response, confidence, human_attr, bot_attr, attr = process_info(dialog, which_info="name")

        if confidence == 0.0:
            response, confidence, human_attr, bot_attr, attr = process_info(dialog, which_info="homeland")

        if confidence == 0.0:
            response, confidence, human_attr, bot_attr, attr = process_info(dialog, which_info="location")

        if confidence == 0.0:
            response, confidence, attr = tell_my_info(dialog, which_info="name")

        if confidence == 0.0:
            response, confidence, attr = tell_my_info(dialog, which_info="location")

        if confidence == 0.0:
            response, confidence, attr = tell_my_info(dialog, which_info="homeland")

        responses.append(response)
        confidences.append(confidence)
        human_attributes.append(human_attr)
        bot_attributes.append(bot_attr)
        attributes.append(attr)

    total_time = time.time() - st_time
    logger.info(f'personal_info_skill exec time: {total_time:.3f}s')
    return jsonify(list(zip(responses, confidences, human_attributes, bot_attributes, attributes)))


what_is_your_name_pattern = re.compile(
    r"((what is|what's|whats|tell me|may i know|ask you for) your? name|what name would you like)", re.IGNORECASE)
my_name_is_pattern = re.compile(r"(my (name is|name's)|call me)", re.IGNORECASE)
_is_not_re = r"(is not|isn't|was not|wasn't|have (not|never) been|haven't been|had (not|never) been|hadn't been)"
my_name_is_not_pattern = re.compile(
    rf"my (name is not|name {_is_not_re}|name's not)|not call me|why do you call me|"
    rf"(that|this|it) {_is_not_re} my name",
    re.IGNORECASE)
where_are_you_from_pattern = re.compile(r"(where are you from|where you (were|was) born|"
                                        r"(what is|what's|whats|tell me) your "
                                        r"(home\s?land|mother\s?land|native\s?land|birth\s?place))", re.IGNORECASE)
my_origin_is_pattern = re.compile(r"(my ((home\s?land|mother\s?land|native\s?land|birth\s?place) "
                                  r"is|(home\s?land|mother\s?land|native\s?land|birth\s?place)'s)|"
                                  r"(i was|i were) born in|i am from|i'm from)", re.IGNORECASE)
what_is_your_location_pattern = re.compile(r"((what is|what's|whats|tell me) your? location|"
                                           r"where do you live|where are you now|"
                                           r"is that where you live now)", re.IGNORECASE)
my_location_is_pattern = re.compile(r"(my (location is|location's)|(i am|i'm|i)( live| living)? in([a-zA-z ]+)?now)",
                                    re.IGNORECASE)

_name_re = r"(first |last |middle |second )?name"
_tell_re = r"((told|said|gave)|(tells|says|gives)|((have|had) (told|said|given)))"
_you_know_question_re = \
    r"((do|did|can|could) you (know|find out|learn)|(have|had) you (known|found out|learned|learnt))"
_how_re = r"(how|where|when|from whom)"
_i_live_re = r"(i lived?|my (house|home) (is|was|have been)|my family live[sd]?)"
_how_do_you_know_question = rf"({_how_re} {_you_know_question_re}|who {_tell_re} you)"
how_do_you_know_my_info_patterns = {
    "name": re.compile(rf"{_how_do_you_know_question} (my {_name_re}|what is my {_name_re}|what my {_name_re} is)"),
    "location": re.compile(rf"{_how_do_you_know_question} where {_i_live_re}"),
    "homeland": re.compile(rf"{_how_do_you_know_question} where i am from")
}
BOT_DOESNT_KNOW_INFO_KEY = "bot_doesnt_know_info"
BOT_KNOWS_INFO_KEY = "bot_knows_info"
how_do_you_know_my_info_responses = {
    "name": {
        BOT_DOESNT_KNOW_INFO_KEY: "Sorry, but I really do not know your name. "
        "Would you be so kind to tell me you name?",
        BOT_KNOWS_INFO_KEY: "Ah, you have probably forgotten that you told me your name before. "
        "Maybe you told me your name the last time we talked.",
    },
    "location": {
        BOT_DOESNT_KNOW_INFO_KEY: "Sorry, but I really do not know where you live. Would tell me?",
        BOT_KNOWS_INFO_KEY: "Ah, you have probably forgotten that"
        "you told me where you live before. Maybe you told me this the last time we talked.",
    },
    "homeland": {
        BOT_DOESNT_KNOW_INFO_KEY: "Sorry, but I really do not know where you are from. "
        "So, where are you from? I hope i am not tactless.",
        BOT_KNOWS_INFO_KEY: "Ah, you have probably forgotten that you told me where you are from before. "
        "Maybe you told me this the last time we talked",
    }
}
MAX_READABLE_NAME_WORD_LEN = 20


def filter_unreadable_names(found_name):
    words = found_name.split()
    max_word_len = max([len(w) for w in words])
    if max_word_len > MAX_READABLE_NAME_WORD_LEN or len(words) > 4:
        filtered_result = None
    else:
        filtered_result = found_name
    return filtered_result


def shorten_long_names(found_name):
    words = found_name.split()
    if len(words) > 2:
        shortened_result = words[0]
    else:
        shortened_result = found_name
    return shortened_result


def process_info(dialog, which_info="name"):
    human_attr = {}
    bot_attr = {}
    attr = {"can_continue": CAN_NOT_CONTINUE}
    response = ""
    confidence = 0.0

    curr_uttr_dict = dialog["human_utterances"][-1]
    curr_user_uttr = curr_uttr_dict["text"].lower()
    curr_user_annot = curr_uttr_dict["annotations"]
    bot_utterance_texts = [u['text'].lower() for u in dialog["bot_utterances"]]
    try:
        prev_bot_uttr = dialog["bot_utterances"][-1]["text"].lower()
    except IndexError:
        prev_bot_uttr = ""

    logger.info(f"Previous bot uuterance: {prev_bot_uttr}")
    is_about_templates = {
        "name": what_is_your_name_pattern.search(prev_bot_uttr) or my_name_is_pattern.search(curr_user_uttr),
        "homeland": where_are_you_from_pattern.search(prev_bot_uttr) or my_origin_is_pattern.search(curr_user_uttr),
        "location": what_is_your_location_pattern.search(prev_bot_uttr) or my_location_is_pattern.search(curr_user_uttr)
    }
    repeat_info_phrases = {"name": "I didn't get your name. Could you, please, repeat it.",
                           "location": "I didn't get your location. Could you, please, repeat it.",
                           "homeland": "I didn't get where you have been born. Could you please repeat it?"}

    response_phrases = {"name": ["Nice to meet you, "],
                        "location": [ASK_WEATHER_SKILL_FOR_HOMELAND_PHRASE, "Cool!"],
                        "homeland": ["Is that where you live now?", "Cool!"]}
    response_phrases = {
        "name": response_phrases["name"][0],
        "location": response_phrases["location"][1] if response_phrases["location"][0].lower() in bot_utterance_texts
        else response_phrases["location"][0],
        "homeland": response_phrases["homeland"][1] if response_phrases["homeland"][0].lower() in bot_utterance_texts
        else response_phrases["homeland"][0],
    }

    got_info = False
    # if user doesn't want to share his info
    if (is_about_templates[which_info] or prev_bot_uttr == repeat_info_phrases[
        which_info].lower()) and curr_user_annot.get(
            "intent_catcher", {}).get("no", {}).get("detected", 0) == 1:
        response = "As you wish."
        confidence = 1.0
        attr["can_continue"] = CAN_NOT_CONTINUE
        return response, confidence, human_attr, bot_attr, attr

    if re.search(r"is that where you live now", prev_bot_uttr) and is_yes(curr_uttr_dict):
        logger.info(f"Found location=homeland")
        if dialog["human"]["attributes"].get("homeland", None):
            human_attr["location"] = dialog["human"]["attributes"]["homeland"]
        else:
            found_homeland = check_entities("homeland",
                                            curr_user_uttr=dialog["utterances"][-3]["text"].lower(),
                                            curr_user_annot=dialog["utterances"][-3]["annotations"],
                                            prev_bot_uttr=dialog["utterances"][-4]["text"].lower())
            human_attr["location"] = found_homeland
        response = response_phrases["location"]
        confidence = 1.0
        got_info = True
        attr["can_continue"] = MUST_CONTINUE
    elif re.search(r"is that where you live now", prev_bot_uttr) and is_no(curr_uttr_dict):
        logger.info(f"Found location is not homeland")
        response = f"So, where do you live now?"
        confidence = 1.0
        got_info = False
        attr["can_continue"] = MUST_CONTINUE

    if my_name_is_not_pattern.search(curr_user_uttr):
        logger.info(f"User says My name is not Blabla")
        response = f"My bad. What is your name again?"
        confidence = 1.0
        got_info = True
        attr["can_continue"] = MUST_CONTINUE

    if (is_about_templates[which_info] or prev_bot_uttr == repeat_info_phrases[which_info].lower()) and not got_info:
        logger.info(f"Asked for {which_info} in {prev_bot_uttr}")
        found_info = check_entities(which_info, curr_user_uttr, curr_user_annot, prev_bot_uttr)
        logger.info(f"found_info: {found_info}")
        if which_info == "name" and found_info is not None:
            found_info = filter_unreadable_names(found_info)
        if found_info is None:
            logger.info(f"found_info is None")
            if prev_bot_uttr == repeat_info_phrases[which_info].lower():
                response = ""
                confidence = 0.0
                attr["can_continue"] = CAN_NOT_CONTINUE
            elif which_info == "name" and len(curr_user_uttr.split()) == 1 and \
                    len(get_entities(curr_uttr_dict, only_named=False, with_labels=False)) > 0:
                response = "I've never heard about this name."
                confidence = 1.0
                attr["can_continue"] = MUST_CONTINUE
            else:
                response = repeat_info_phrases[which_info]
                confidence = 1.0
                attr["can_continue"] = MUST_CONTINUE
        else:
            if which_info == "name":
                found_info = shorten_long_names(found_info)
                response = response_phrases[which_info] + found_info + "."
            elif which_info == "location":
                response = response_phrases[which_info]
            elif which_info == "homeland":
                if dialog["human"]["profile"].get("location", None) is None:
                    response = response_phrases[which_info]
                else:
                    response = response_phrases["location"]
            human_attr[which_info] = found_info
            confidence = 1.0
            attr["can_continue"] = MUST_CONTINUE

    return response, confidence, human_attr, bot_attr, attr


def how_do_you_know_my_info(dialog, which_info="name"):
    curr_user_uttr = dialog["utterances"][-1]["text"].lower()
    how_do_you_know_search_result = how_do_you_know_my_info_patterns[which_info].search(curr_user_uttr)
    if how_do_you_know_search_result is None:
        response = ""
        confidence = 0.0
        attr = {}
    else:
        if dialog.get("human", {}).get("profile", {}).get(which_info, ""):
            response = how_do_you_know_my_info_responses[which_info][BOT_KNOWS_INFO_KEY]
        else:
            response = how_do_you_know_my_info_responses[which_info][BOT_DOESNT_KNOW_INFO_KEY]
        confidence = 1.0
        attr = {"can_continue": MUST_CONTINUE}
    return response, confidence, attr


def tell_my_info(dialog, which_info="name"):
    response = ""
    confidence = 0.0
    attr = {}

    curr_user_uttr = dialog["utterances"][-1]["text"].lower()

    tell_my_templates = {"name": re.search(r"((what is|what's|whats|tell me|you know|you remember|memorize|say) "
                                           r"my name|"
                                           r"how( [a-zA-z ]+)?call me)",
                                           curr_user_uttr),
                         "location": re.search(r"((what is|what's|whats|tell me|you know|you remember|memorize|say) "
                                               r"my (location|country|city|town)|"
                                               r"where (am i|i am)(\snow)?|"
                                               r"where( do)?i live|where( am)?i( am)? living)|"
                                               r"(what|which) (country|city|town)( do)? (i|am i|i am)",
                                               curr_user_uttr),
                         "homeland": re.search(r"((what is|what's|whats|tell me|you know|you remember|memorize|say) "
                                               r"my (home\s?land|mother\s?land|home\s?town|native\s?land"
                                               r"|birth\s?place)|"
                                               r"where (am i|i am) from)",
                                               curr_user_uttr)}

    responses = {"name": f"Sorry, we are still not familiar. What is your name?",
                 "location": f"Sorry, I don't have this information. But you can tell me. What is your location?",
                 "homeland": f"Sorry, I don't have this information. But you can tell me. Where are you from?"}
    if tell_my_templates[which_info]:
        logger.info(f"Asked to memorize user's {which_info} in {curr_user_uttr}")
        if dialog["human"]["profile"].get(which_info, None) is None:
            response = responses[which_info]
            confidence = 1.0
            attr["can_continue"] = MUST_CONTINUE
        else:
            name = dialog["human"]["profile"][which_info]
            response = f"Your {which_info} is {name}."
            confidence = 1.
            attr["can_continue"] = MUST_CONTINUE
    return response, confidence, attr


def extract_possible_names(annotated_utterance, only_named, with_labels):
    entities = get_entities(
        annotated_utterance,
        only_named=only_named,
        with_labels=with_labels,
    )
    if not only_named:
        nounphrases = annotated_utterance["annotations"].get("cobot_nounphrases", [])
        if with_labels:
            nounphrases = [{"text": np, "label": "misc"} for np in nounphrases]
        entities += nounphrases
    return entities


def check_entities(which_info, curr_user_uttr, curr_user_annot, prev_bot_uttr):
    found_info = None

    if which_info == "name":
        named_entities = get_named_persons({"text": curr_user_uttr, "annotations": curr_user_annot})
    else:
        named_entities = get_named_locations({"text": curr_user_uttr, "annotations": curr_user_annot})
    logger.info(f"(check_entities)named_entities: {named_entities}")
    if len(named_entities) == 0:
        # try to search in all types of NAMED entities
        named_entities = []
        for ent in extract_possible_names(
                {"text": curr_user_uttr, "annotations": curr_user_annot},
                only_named=False,
                with_labels=True,
        ):
            logger.info(f"(check_entities)ent: {ent}")
            if "my name is" == ent["text"].lower() or "call me" == ent["text"].lower():
                continue
            if ent["text"].lower() == "alexa":
                if (re.search(r"(my (name is|name's)|call me) alexa", curr_user_uttr) or (re.search(
                        r"(what is|what's|whats|tell me) your? name",
                        prev_bot_uttr) and re.match(r"^alexa[.,!?]*$", curr_user_uttr))):
                    # - my name is alexa
                    # - what's your name? - alexa.
                    pass
                else:
                    # in all other cases skip alexa
                    continue
            if re.search(
                    r"^" + ent["text"] + r"[.,!?]*$|" + my_name_is_pattern.pattern + ' +' + ent["text"],
                    curr_user_uttr,
                    re.IGNORECASE
            ):
                named_entities.append(ent["text"])
            elif (which_info == "name" and ent.get("type", "") == "PER") or (
                    which_info in ["homeland", "location"] and ent.get("type", "") == "LOC"):
                named_entities.append(ent["text"])

    if named_entities:
        ent = named_entities[-1]
        found_info = " ".join([n.capitalize() for n in ent.split()])
    logger.info(f"Found {which_info} `{found_info}`")
    return found_info


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=3000)
