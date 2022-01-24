# -*- coding: utf-8 -*-
"""
Created on Mon Jan 24 19:12:50 2022

@author: tobycrisford

I explain in the readme that I've chosen not to make use of the separate list of solutions
in Wordle's source code. It seemed more in the spirit of the game to assume
that any valid guess could be the answer. However, in this script I drop that
constraint, as an experiment (and so this script can be integrated with other people's
solvers which also don't use this constraint).
"""

import wordle_solver
import numpy as np

with open('wordle_dictionary.txt', 'r') as f:
    raw_text = f.readlines()
    
def clean_line(l):
    word_list = []
    split_line = l.split('"')
    for w in split_line:
        word = w.replace('[','')
        word = w.replace(',','')
        if len(word) == 5:
            word_list.append(word)
    return word_list
        
possible_solutions = clean_line(raw_text[0])
possible_guesses = clean_line(raw_text[1])

initial_word_list = np.array(possible_guesses + possible_solutions)

current_word_list = np.array(possible_solutions)

frequency_dict = dict()
for w in initial_word_list:
    frequency_dict[w] = 1
    
print("Your next guess should be soare")
next_guess = "soare"

while True:
    
    result = input("What was the result? -=grey, .=orange, *=green:")
    current_word_list = wordle_solver.update_word_list(current_word_list, next_guess, result)
    if len(current_word_list) == 1:
        print("The word is: " + current_word_list[0])
        break
    
    print("There are " + str(len(current_word_list)) + " words remaining.")
    suggestions, info_scores = wordle_solver.get_suggestions_brutish_force(initial_word_list, current_word_list, frequency_dict)
    next_guess = initial_word_list[suggestions[0]]
    print("Your next guess should be " + next_guess)
