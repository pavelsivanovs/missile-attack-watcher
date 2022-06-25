import asyncio
import csv
import os
import re

import telethon.client
from dotenv import load_dotenv
import pymorphy2
import stanza
from telethon import TelegramClient
from translitua import translit


# WORK PLAN
# 1. [DONE] subscribe to the news channel
# 2. [DONE] extract messages into the text files
# 3. [DONE] use Stanza to commit NER
# 4. Lemmatize locations
# 5. [DONE] Transliterate locations from Cyrillic to Latin
# 6. Aggregate information

# TODO: Implement a file with the list of the channels to get info from
# TODO: Proceed with NER only to the sentences where the keywords are
# TODO: Test lemmatize()
# TODO: Aggregate information as 5 most mentioned locations in the reports or sth like that.
#  Maybe can use some graphs for this sake.

async def get_dialogs(client: telethon.client.TelegramClient, filename: str):
    """
    Gets the list of dialogs via Telegram client and writes it into the file

    :param client: Telegram client.
    :param filename: name of the CSV file.
    """

    with open(filename, mode='w', encoding='UTF8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['ID', 'DIALOG NAME'])

        async for dialog in client.iter_dialogs():
            if dialog.name:
                writer.writerow([dialog.id, dialog.name])


def lemmatize(text: str) -> str:
    """
    Lemmatizes the provided string to the normal form, i.e., Nominative. As well, inflects the adjectives to the
    provided noun in the text. E.g., "Херсонський область" -> "Херсонська область"

    :param text: string to be lemmatized and inflected.
    :return: lemmatized and inflected text.
    """

    doc = nlp(text)
    doc_len = len(doc.entities[0].tokens)
    last_token = morph.parse(doc.entities[0].tokens[doc_len - 1].text)[0].normalized
    lemmatized = last_token.word

    if doc_len > 1:
        gender = last_token.tag.gender

        if gender:
            inflected = ''

            for i in range(0, doc_len - 1):
                p = morph.parse(doc.entities[0].tokens[i].text)[0]
                inflected += p.inflect({gender}).word

            lemmatized = inflected + lemmatized

    return lemmatized.capitalize()


async def main():
    client = TelegramClient('test_session', api_id, api_hash)
    await client.start()

    # RETRIEVING THE LIST OF DIALOGS
    # await get_dialogs(client, 'dialogs.csv')

    # RETRIEVING MESSAGES FROM THE CHANNEL
    regex = r'(ракет)|(удар)'

    with open('attempt.csv', mode='w', encoding='UTF8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['MESSAGE ID', 'MESSAGE TEXT', 'DATETIME', 'LOCATION ENTITIES'])

        async for message in client.iter_messages(PRIAMYI, limit=400):
            if message.message and re.search(regex, message.message):
                doc = nlp(message.message)
                locations = []

                for entity in doc.entities:
                    if entity.type == 'LOC':
                        loc_text = translit(morph.parse(entity.text)[0].normalized.word.capitalize())
                        locations.append(loc_text)

                writer.writerow([message.id, message.message, message.date, locations])


load_dotenv()

PRIAMYI = -1001117030092
api_id = os.getenv('TELEGRAM_API_ID')
api_hash = os.getenv('TELEGRAM_API_HASH')

morph = pymorphy2.MorphAnalyzer(lang='uk')
stanza.download('uk')
nlp = stanza.Pipeline('uk')

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  # needed to resolve the exception
asyncio.run(main())
