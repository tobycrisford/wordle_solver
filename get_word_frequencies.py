# -*- coding: utf-8 -*-
"""
Created on Fri Jan 14 17:24:04 2022

@author: tobycrisford

This script extracts word frequencies for your chosen word list
from the files found here: http://storage.googleapis.com/books/ngrams/books/datasetsv2.html
and saves them in a pickle for convenient extraction during the game.
"""

from wordle_dictionary import get_full_word_list
from tqdm import tqdm
import requests
import pickle
import time
import os

filename = 'wordle_dictionary.txt'
word_length = 5

word_list = get_full_word_list(filename,word_length)

word_set = set(word_list)

frequency_dict = dict()

for f in os.listdir('./word_frequencies'):
    with open('word_frequencies/' + f + '/' + f, encoding='utf-8') as file:
        for line in tqdm(file):
            row = line.split("\t")
            if row[0] in word_set:
                if row[0] in frequency_dict:
                    frequency_dict[row[0]] += int(row[2])
                else:
                    frequency_dict[row[0]] = int(row[2])

pickle.dump(frequency_dict, open(filename + "." + str(word_length) + ".pkl","wb"))