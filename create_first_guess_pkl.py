# -*- coding: utf-8 -*-
"""
Created on Sat Jan 15 11:12:04 2022

@author: tobycrisford
"""

from wordle_solver import preprocess_word_frequencies, get_suggestions_brutish_force
import numpy as np
from wordle_dictionary import get_full_word_list
import pickle

initial_word_list = np.array(get_full_word_list("wordle_dictionary.txt", 5))
    
frequency_dict = preprocess_word_frequencies("wordle_dictionary.txt.5.pkl", initial_word_list)

suggestions, info_scores = get_suggestions_brutish_force(initial_word_list, initial_word_list, frequency_dict)

pickle.dump((initial_word_list[suggestions], info_scores), open('first_guess.pkl','wb'))