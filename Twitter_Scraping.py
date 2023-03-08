import snscrape.modules.twitter as sntwitter
from pymongo import MongoClient
import json
import base64
import streamlit as st
import pandas as pd


# Function to scrape Twitter data and return a list of dictionaries
def scrape_twitter_data(keyword, start_date, end_date, tweet_count):
    # Create a list to store the scraped data
    scraped_data = []
    
    # Define the search query
    search_query = f"{keyword} since:{start_date} until:{end_date}"
    
    # Loop through the Twitter search results and extract the data
    for i, tweet in enumerate(sntwitter.TwitterSearchScraper(search_query).get_items()):
        if i >= tweet_count:
            break
        
        # Extract the tweet data
        tweet_data = {
            "date": tweet.date,
            "id": tweet.id,
            "url": tweet.url,
            "content": tweet.content,
            "user": tweet.user.username,
            "reply_count": tweet.replyCount,
            "retweet_count": tweet.retweetCount,
            "language": tweet.lang,
            "source": tweet.sourceLabel,
            "like_count": tweet.likeCount
        }
        
        # Append the tweet data to the scraped_data list
        scraped_data.append(tweet_data)
        
    return scraped_data

def create_df(scraped_data):
    tweet_data=pd.DataFrame(scraped_data,columns=["date","id","url","content","user","reply_count","retweet_count","Language","source","like_count"])        
    return tweet_data

# GUI.py
st.title("Scrape the Tweets")

# Get input from user for hashtag
keyword = st.text_input("Enter the hashtag:")

# Get starting date from user
start_date = st.date_input("Select start date:", key="start_date")

# Get end date from user
end_date = st.date_input("Select end date:", key="end_date")

# Get tweet limit from user
tweet_count = st.number_input("Enter the number of tweet you need:", key="limit")

# Scrape tweets
if st.button("Scrape Tweets"):
    scraped_data = scrape_twitter_data(keyword, start_date, end_date, tweet_count)
    tweet_data = create_df(scraped_data)
    st.dataframe(tweet_data)
    
    # Download as csv
    st.write("Saving dataframe as csv")
    csv = tweet_data.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="tweet_data.csv">Download CSV File</a>'
    st.markdown(href, unsafe_allow_html=True)
    
    # Download as JSON
    st.write("Saving dataframe as json")
    json_string = tweet_data.to_json(indent=2)
    b64 = base64.b64encode(json_string.encode()).decode()
    href = f'<a href="data:file/json;base64,{b64}" download="tweet_data.json">Download JSON File</a>'
    st.markdown(href, unsafe_allow_html=True)

    # Upload to MongoDB
if st.button("Upload to MongoDB"):
    tweet = scrape_twitter_data(keyword, start_date, end_date, tweet_count)
    tweet_data = create_df(tweet)

    client = MongoClient('mongodb://sharma1204:sharma1204@ac-dqtoutk-shard-00-00.oeojj5f.mongodb.net:27017,ac-dqtoutk-shard-00-01.oeojj5f.mongodb.net:27017,ac-dqtoutk-shard-00-02.oeojj5f.mongodb.net:27017/?ssl=true&replicaSet=atlas-6lfbkt-shard-0&authSource=admin&retryWrites=true&w=majority')
    db = client["twitter_db_streamlit"]
    collection = db['tweet']
    tweet_data_json = json.loads(tweet_data.to_json(orient='records'))
    collection.insert_many(tweet_data_json)
    st.success('Uploaded to MongoDB')

# Download as csv
if st.button("Download as CSV"):
    tweet = scrape_twitter_data(keyword, start_date, end_date, tweet_count)
    tweet_data = create_df(tweet)
    st.write("Saving dataframe as csv")
    csv = tweet_data.to_csv(index=False)
    print(csv) # print the content of the CSV data
    b64 = base64.b64encode(csv.encode()).decode()
    print(b64) # print the encoded data
    href = f'<a href="data:file/csv;base64,{b64}"download="tweet_data.csv">Download CSV File</a>'
    st.markdown(href, unsafe_allow_html=True)

# Download as JSON
if st.button("Download as Json"):
    tweet = scrape_twitter_data(keyword, start_date, end_date, tweet_count)
    tweet_data = create_df(tweet)
    st.write("Saving dataframe as json")
    json_string = tweet_data.to_json(indent=2)
    print(json_string) # print the content of the JSON data
    b64 = base64.b64encode(json_string.encode()).decode()
    print(b64) # print the encoded data
    href = f'<a href="data:file/json;base64,{b64}"download="tweet_data.json">Download json File</a>'
    st.markdown(href, unsafe_allow_html=True)