"""
:author Pavels Ivanovs <pavelsivanovs.lv@gmail.com>
"""

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


async def main(output_filename='telegram.csv'):
    client = TelegramClient('test_session', api_id, api_hash)
    await client.start()

    # RETRIEVING MESSAGES FROM THE CHANNEL
    print('Writing into', output_filename)

    with open(output_filename, mode='w', encoding='UTF8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['PLATFORM', 'SOURCE','MESSAGE TEXT', 'DATETIME', 'LOCATIONS'])

        with open('dialogs.csv', encoding='UTF8', newline='') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:

                print('Analyzing data from', row['DIALOG_NAME'])

                async for message in client.iter_messages(int(row['ID']), limit=500):
                    # Filtering out the messages which do not have required keywords
                    if message.message and re.search(r'([Рр]акет)|([Уу]дар)', message.message):
                        doc = nlp(message.message)
                        locations = []

                        for tok in doc.iter_tokens():
                            token = tok

                            # If the location entity is one-word long
                            if token.ner == 'S-LOC':
                                # We are storing location name lemmas
                                location = translit(token.words[0].lemma).upper()

                                # Checking if the location is not in the black list of toponyms, e.g., countries
                                if location not in black_list:
                                    locations.append(location)

                            # Meaning that location entity contains of several tokens
                            # B-LOC means that this is a first token in location entity chunk
                            elif token.ner == 'B-LOC':
                                # As well, storing the lemma only for better inflection later
                                bloc = token.words[0].lemma
                            elif token.ner == 'E-LOC': # The last token of location entity
                                gender = 'Masc' # Default gender

                                # Extracting the gender from the grammatical features of the token word
                                if re.findall(r'Gender=(\w*)', token.words[0].feats):
                                    gender = re.findall(r'Gender=(\w*)', token.words[0].feats)[0]

                                # Parsing the B-LOC to morphological analyzer
                                p = morph.parse(bloc)[0]

                                # Inflecting the B-LOC to have the same gender as E-LOC
                                if p is not None:
                                    if gender == 'Masc' and p.inflect({'masc'}) is not None:
                                        bloc = p.inflect({'masc'}).word
                                    elif gender == 'Fem' and p.inflect({'femn'}) is not None:
                                        bloc = p.inflect({'femn'}).word
                                    elif gender == 'Neut' and p.inflect({'neut'}) is not None:
                                        bloc = p.inflect({'neut'}).word

                                location = translit(bloc + ' ' + token.words[0].lemma).upper()

                                if location not in black_list:
                                    locations.append(location)

                        writer.writerow(['Telegram', row['DIALOG_NAME'], message.message, message.date, locations]) \
                            if locations else None


if __name__ == '__main__':
    # Retrieving API keys
    load_dotenv()
    api_id = os.getenv('TELEGRAM_API_ID')
    api_hash = os.getenv('TELEGRAM_API_HASH')

    print('Installing NLP libraries')

    # Installing NLP modules
    morph = pymorphy2.MorphAnalyzer(lang='uk')
    stanza.download('uk')
    # path to trained NER model
    nlp = stanza.Pipeline('uk', ner_model_path='stanza/saved_models/ner/uk_languk_nertagger.pt')

    # Blacklist of locations not to be included in the output file
    black_list = ['UKRAINA', 'SSHA', 'BILORUS', 'ROSIIA', 'POLSHCHA', 'YEVROPA', 'NPZ', 'ZRK', 'RF', 'NIMECHCHYNA',
                  'LYTVA', 'SHVETSIIA', 'TURECHCHYNA', 'ISPANIIA', 'FRANTSIIA', 'BLYZKYI SKHID', 'HENSHTAB']

    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  # needed to resolve the exception
    asyncio.run(main('telegram.csv'))
