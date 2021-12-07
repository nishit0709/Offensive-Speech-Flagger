from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
ps = PorterStemmer()



from tensorflow.keras.models import model_from_json
json_file = open(r'C:\Users\Rupin Patel\Documents\GitHub\vigilant-octo-broccoli\Detector/model.json', 'r') #load model
loaded_model_json = json_file.read()
json_file.close()
loaded_model = model_from_json(loaded_model_json)
loaded_model.load_weights(r"C:\Users\Rupin Patel\Documents\GitHub\vigilant-octo-broccoli\Detector/model.h5") #load weights
loaded_model.compile(loss='binary_crossentropy',optimizer='adam',metrics=['accuracy']) 



import json
from keras_preprocessing.text import tokenizer_from_json
with open(r'C:\Users\Rupin Patel\Documents\GitHub\vigilant-octo-broccoli\Detector/tokenizer.json') as f:
    data = json.load(f)
    tokenizer = tokenizer_from_json(data) #load tokenizer

stop_words = set(stopwords.words("english"))


import pandas as pd
df = pd.read_csv(r"C:\Users\Rupin Patel\Documents\GitHub\vigilant-octo-broccoli\Detector/Hinglish_Profanity_List.csv")
bad_words = dict(zip(df.Hinglish,df.English))