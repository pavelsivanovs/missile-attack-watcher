import tweepy
import spacy
from csv import writer

consumer_key = 'BcyX0H6hZIdJisxis9NK46wDp'
consumer_secret = '1GVKixoVzdKsfPyi95NYqqALqxJAL08Q5nh3hIfzYTkSYyGUCB'
access_key = '1009368854-BEyMcqdZbIzIsG0iiV5ic4Mv5BA2Nx7AiiStZt3'
access_secret = 'iI5DM5A0iwDvCBL6Q49zaTCWMEtRqm46XNOq5nPc534mh'


def append_list_as_row(file_name, list_of_elem):
    # Open file in append mode
    with open(file_name, 'a+', encoding='UTF8', newline='') as write_obj:
        # Create a writer object from csv module
        csv_writer = writer(write_obj)
        # Add contents of list as last row in the csv file
        csv_writer.writerow(list_of_elem)

# Function to extract tweets

def get_tweets(username: str):
    """
    Function to extract tweets.
    """

    # twitter Bearer token
    client = tweepy.Client(
        'AAAAAAAAAAAAAAAAAAAAAPgScgEAAAAAhZVcTpWmaxH%2BpQ2Fj0TXFOsTAfc%3DHNYb0bKgpCtcm52FuscOj5wCXHmcX8DgA0I3BIyebGqp7qFhDx')
    # finds the selected accounts data
    user_id = client.get_user(username=username)
    # finds a selected ammount of tweet text and the corresponding timestamps
    result = client.get_users_tweets(id=user_id.data.id, tweet_fields="text,created_at,id", max_results=100)
    tweettoup = []
    # keywords used for selecting tweets about attacks
    contextkey=["missile", "Missile", "shelling", "strike", "Shelling", "Strike"]
    for i in [1,2,3,4,5,6,7,8,9]:
        batchnr = 0
        batchid = 0
        for k in result.data:
            batchnr=batchnr+1
            # Appending tweets to the empty array tmp
            if any(key in k.text for key in contextkey):
                tweettoup.append((k.text, k.created_at))
            if batchnr==100:
                batchid=k.id
        result = client.get_users_tweets(id=user_id.data.id, tweet_fields="text,created_at,id", max_results=100, until_id=batchid)
    for k in result.data:
        # Appending tweets to the empty array tmp
        if any(key in k.text for key in contextkey):
            tweettoup.append((k.text, k.created_at))
    # Loading the named entity recognizer
    NER = spacy.load('en_core_web_lg')
    # skip list for entities that are known but should not appear in the results
    ent_skip = ["Russia", "Ukraine", "Belarus", "Moscow", "Minsk", "Energoatom", "Ukrainian", "Igla", "Latvia", "US", "Poland", "Belgium", "Netherlands", "Germany", "Italy", "Turkey", "Estonia"
                , "Romania", "Iohannis", "Denmark", "UK", "The Czech Republic", "U.S.", "Israel", "Sweden", "Czechia", "Egypt"]
    for a in tweettoup:
        doc = NER(a[0])
        enttmp = []
        # checking if tweet text contains any entities
        if doc.ents:
            for ent in doc.ents:
                # GPE Geopolitical entity
                if (ent.text not in ent_skip) and ent.label_ == "GPE":
                    enttmp.append(ent.text)
                    # print(ent.text +' - '+ ent.label_)
        # append results to output.csv
        if enttmp:
            append_list_as_row('output.csv', ["Twitter", username, a[0], a[1], enttmp])


# Driver code
if __name__ == '__main__':
    # Here goes the Twitter handle for the user
    # whose tweets are to be extracted.
    get_tweets('KyivIndependent')
