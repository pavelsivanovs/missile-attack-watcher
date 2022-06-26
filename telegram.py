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

    # RETRIEVING THE LIST OF DIALOGS
    # await get_dialogs(client, 'dialogs.csv')

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
                    if message.message and re.search(r'([Рр]акет)|([Уу]дар)', message.message):
                        doc = nlp(message.message)
                        locations = []

                        for tok in doc.iter_tokens():
                            token = tok

                            if token.ner == 'S-LOC':
                                location = translit(token.words[0].lemma).upper()

                                if location not in black_list:
                                    locations.append(location)

                            # Meaning that location entity contains of several tokens
                            elif token.ner == 'B-LOC':
                                bloc = token.words[0].lemma
                            elif token.ner == 'E-LOC': # The last token of location entity
                                gender = 'Masc' # Default gender
                                if re.findall(r'Gender=(\w*)', token.words[0].feats):
                                    gender = re.findall(r'Gender=(\w*)', token.words[0].feats)[0]
                                p = morph.parse(bloc)[0]

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
    load_dotenv()

    api_id = os.getenv('TELEGRAM_API_ID')
    api_hash = os.getenv('TELEGRAM_API_HASH')

    print('Installing NLP libraries')

    morph = pymorphy2.MorphAnalyzer(lang='uk')
    stanza.download('uk')
    nlp = stanza.Pipeline('uk', ner_model_path='stanza/saved_models/ner/uk_languk_nertagger.pt')

    black_list = ['UKRAINA', 'SSHA', 'BILORUS', 'ROSIIA', 'POLSHCHA', 'YEVROPA', 'NPZ', 'ZRK', 'RF', 'NIMECHCHYNA',
                  'LYTVA', 'SHVETSIIA', 'TURECHCHYNA', 'ISPANIIA', 'FRANTSIIA', 'BLYZKYI SKHID', 'HENSHTAB'
                  'skhod', 'Shvetsiia', 'Finliandiia', 'Izrail', 'Syriia', 'Irak', 'Turechchyna', 'ova', 'ovyi',
                  'Henshtab', 'Rf', 'Yes']

    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  # needed to resolve the exception
    asyncio.run(main('telegram.csv'))
