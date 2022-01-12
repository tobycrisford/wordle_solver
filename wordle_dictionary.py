# -*- coding: utf-8 -*-
"""
Created on Tue Jan 11

@author: tobycrisford

Actual word list used by wordle
"""

#Word lists have been extracted from the Wordle game javascript source code.
#They need some cleaning, which is done here.

def get_full_word_list(dict_file, word_length):

    with open(dict_file, 'r') as f:
        raw_text = f.readlines()
        
    word_list = []
    for l in raw_text:
        split_line = l.split('"')
        for w in split_line:
            word = w.replace('[','')
            word = w.replace(',','')
            if len(word) > 0:
                word_list.append(word)
                
    word_list = [w for w in word_list if len(w) == word_length]

    return list(set(word_list))