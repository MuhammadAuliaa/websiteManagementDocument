import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
import time
import re
import nltk
from nltk.corpus import stopwords
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from translate import Translator
from textblob import TextBlob
import joblib
import tokenizer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def clean(text):
  text = text.lower()
  text = re.sub(r'@[A-Za-z0-9_]+', '', text)
  text = re.sub(r'#\w+', '', text)
  text = re.sub(r'RT[\s]+', '', text)
  text = re.sub(r'https?://\S+', '', text)
  text = re.sub(r'[^A-Za-z0-9 ]', '', text)
  text = re.sub(r'\s+', ' ', text).strip()

  return text  

def filter_tokens_by_length(dataframe, column, min_words, max_words):
    words_count = dataframe[column].astype(str).apply(lambda x: len(x.split()))
    mask = (words_count >= min_words) & (words_count <= max_words)
    filtered_df = dataframe[mask]
    return filtered_df

norm= {' yg ':' yang ', ' udh ':' udah ', 'wkwk ':' ', ' min ':' kak ', ' malem ':' malam', ' malem2 ':' malam ', ' sm ':' sama ', ' dy ':' dia ', ' lg ':' lagi ', ' skrg ':' sekarang ', ' ddpn ':' didepan ', ' makasi ':' makasih ', ' pertamaz ':' pertamax ', ' jg ':' juga ', ' donk ':' dong ', ' ikutann ':' ikutan ', ' banyakk ':' banyak ', ' twt ':' tweet', 'mantaap ':'mantap ', ' juarak':' juara ', 'daridulu ':'dari dulu ', 'siapp ':'siap ', ' gamau ':' tidak mau ', ' sll ':' selalu ', ' qu ':' aku ', ' krn ':' karena ', ' irii':' iri', ' muluu ':' terus ', 'mada ':'masa ', 'jgn ':'jangan ', ' jgn ':' jangan ', ' muluuu ':' terus ', 'ntar ':'nanti ', ' awtnya':' awetnya', 'gg ':'keren ', ' kerennn':' keren ', ' bisaa ':' bisa ', 'gaaa':'tidak ', " yg ": " yang ", ' nyampe':' sampai', ' nyampe ':' sampai ', ' lu ':' kamu ', ' ikhlaaasss ':' ikhlas ', ' gak ':' tidak ', ' klo ':' kalo ', ' amp ': ' sampai ', ' ga ':' tidak ', ' yaaaa':' ya ', 'betolll ':'betul ', ' kaga ':' tidak ', ' idk ':' tidak tahu ', ' jkt ':' jakarta ', ' lo ':' kamu ', ' bjir ':' ', ' kek ':' seperti ', ' yg ':' yang ', ' utk ':' untuk ', 'kismin ':'miskin ', ' kismin ':' miskin ', ' pd ':' pada ', ' dgn ':' dengan ', ' ituu ':' itu ', ' jg ':' juga ', 'yoi':'iya ', ' yoi ':' iya ', 'org2 ':'orang ', ' tak ':' tidak ', ' kyk ':' seperti ', ' sbg ':' sebagai ', ' anjjjj ':' ', ' bgt ':' banget ', 'km ':'kamu ', ' km ':' kamu', ' byk ':' banyak ', ' lg ':' lagi ', ' mrk ':' mereka ', ' blm ':' belum ', ' emg ':' emang ', ' nich ':' ini '}

def normalisasi(text):
  for i in norm:
    text = text.replace(i, norm[i])
  return text

def stopword(text):
    stop_words = set(stopwords.words('indonesian'))
    words = text.split()
    filtered_words = [word for word in words if word.casefold() not in stop_words]
    cleaned_text = ' '.join(filtered_words)
    return cleaned_text

def tokenisasi(text):
    return text.split() 

def stemming(text):
    stemmer = StemmerFactory().create_stemmer()
    text = ' '.join(text)
    stemmed_text = stemmer.stem(text)
    return stemmed_text

def translate_tweet(tweet):
    translator = Translator(to_lang="en", from_lang="id")
    translation = translator.translate(tweet)
    return translation

def getSubjectivity(review) :
    return TextBlob(review).sentiment.subjectivity

def getPolarity(review) :
    return TextBlob(review).sentiment.polarity

def analyze(score):
    if score < 0:
        return 'Negatif'
    else:
        return 'Positif'
    
def merge_and_reset_index(dataframes):
    merged_df = pd.concat(dataframes).drop_duplicates(subset='Message').reset_index(drop=True)
    return merged_df
    
# Function to perform sentiment analysis and save the result
def perform_sentiment_analysis(file_path, data_name):
    try:
        data = pd.read_excel(file_path)
        
        if 'tweet_english' not in data.columns:
            st.warning("Data yang dimasukkan tidak sesuai. Pastikan kolom 'tweet_english' ada dalam file.")
            return None, None

        sentiments = SentimentIntensityAnalyzer()
        data['Positif'] = [sentiments.polarity_scores(i)["pos"] for i in data['tweet_english']]
        data['Negatif'] = [sentiments.polarity_scores(i)["neg"] for i in data['tweet_english']]
        data['Netral'] = [sentiments.polarity_scores(i)["neu"] for i in data['tweet_english']]
        data['Compound'] = [sentiments.polarity_scores(i)["compound"] for i in data['tweet_english']]

        score = data['Compound'].values
        sentiment = []

        for i in score:
            if i >= 0.05:
                sentiment.append("Positif")
            elif i <= -0.05:
                sentiment.append("Negatif")
            else:
                sentiment.append("Netral")

        data["Sentiment(Vader)"] = sentiment

        # Save the labeled data to a new folder with the specified data name
        output_path = "dataHasilLabelingVader/"
        labeled_data_file = f"{data_name}.xlsx"
        data.to_excel(output_path + labeled_data_file, index=False)

        return data, labeled_data_file

    except Exception as e:
        st.warning("Data yang dimasukkan tidak sesuai. Pastikan file Excel valid.")
        return None, None