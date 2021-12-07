import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import re
import preprocessor as p
from keras.preprocessing.sequence import pad_sequences
from Detector import initializer as ini

def regexCleaning(text):
  text = p.clean(text)
  text = re.sub('[^a-zA-Z]| {2,}',' ',text)
  text = text.lower()
  text = text.split() 
  text = [ini.ps.stem(word) for word in text if word not in ini.stop_words]
  text = ' '.join(text)
  if(len(text)):
    return text
  else:
    pass

def translate(sentence):
  translated_sent = ""
  for word in sentence.split():
    if word in ini.bad_words.keys():
      translated_sent += ini.bad_words[word]
    else:
      translated_sent += word +" "
  return translated_sent

def check_tweet(sentence):
  sentence = translate(sentence)
  sentence = [regexCleaning(sentence)]
  if(None in sentence):
    return "Non Offensive"
  seq = ini.tokenizer.texts_to_sequences(sentence)
  seq_padded = pad_sequences(seq, maxlen=50, truncating="post", padding="post")
  prediction = (ini.loaded_model.predict(seq_padded) > 0.5).astype("int32")
  if(prediction):
    return "Offensive"
  else:
    return "Non-Offensive"
