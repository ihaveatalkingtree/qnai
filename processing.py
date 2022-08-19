from tkinter.tix import Tree
import tensorflow as tf
import pandas as pd
from sklearn.model_selection import train_test_split
import numpy as np
from transformers import AutoTokenizer
import re 
import underthesea

strip_special_chars = re.compile("[^\w0-9 ]+")

class TextProcessing:
    def __init__(self, tokenizer, max_length=256, shuffle=False):
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer)
        self.max_length = max_length
        self.shuffle = shuffle
        self.train_features = None
        self.test_features = None
        self.train_labels = None
        self.test_labels = None

    def read_csv(self, name):
        #Convert CSV to List
        data = pd.read_csv(name)
        labels = np.array(data.loc[:, ['giai_tri', 'luu_tru', 'nha_hang', 'an_uong', 'di_chuyen', 'mua_sam']])
        features = data.loc[:, 'Review']
        del data
        X_train, X_test, Y_train, Y_test = train_test_split(features, labels, test_size=0.2)
        self.train_features, self.test_features, self.train_labels, self.test_labels = list(X_train), list(X_test), list(Y_train), list(Y_test)

    def _clean_sentences(self, string):
        string = string.lower().replace("<br />", " ")
        return re.sub(strip_special_chars, "", string.lower())

    def process(self):

        
        #   Clean sentences --> just include digits and numbers. Remove commas, dots, etc...
        self.train_features = [self._clean_sentences(sentence) for sentence in self.train_features]     #   --> Return list: contain each sentence in train set
        self.test_features = [self._clean_sentences(sentence) for sentence in self.test_features]       #   --> Return list: containt each sentence in test set

        #   Tokenize sentences 
        self.train_tokens = [underthesea.word_tokenize(sentence) for sentence in self.train_features]   #   --> Nested List: contain each list of tokenized words
        self.test_tokens = [underthesea.word_tokenize(sentence) for sentence in self.test_features]
        
        # print(self.train_tokens[:5])

        #   Encode string using tokenizer  
        train_encodings = [self.tokenizer(train_tokens, truncation=True, padding=True) for train_tokens in self.train_tokens]    #   --> Return word indices of each tokenized words list
        val_encodings = [self.tokenizer(test_tokens, truncation=True, padding=True)  for test_tokens in self.test_tokens ]    #   --> Return word indices
        
        # print(train_encodings[:5])

        train_dataset = tf.data.Dataset.from_tensor_slices((
            train_encodings,
            self.train_labels
        ))
        val_dataset = tf.data.Dataset.from_tensor_slices((
            val_encodings,
            self.test_labels
        ))
        return train_dataset, val_dataset