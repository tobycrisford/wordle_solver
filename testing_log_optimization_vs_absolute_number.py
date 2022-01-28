# -*- coding: utf-8 -*-
"""
Created on Thu Jan 27 22:05:10 2022

@author: tobycrisford

This is an experiment to demonstrate that minimizing the log of number of remaining
words is better than minimizing the number of remaining words.

For the purposes of this test, I allow both methods to use the list of solutions
from Wordle's source code, which changes the starting words, and makes the use of
word frequencies obsolete. I didn't use this list in the main solver, as it felt like
cheating. See readme for a full discussion.
"""

import wordle_solver
import numpy as np
from tqdm import tqdm
from wordle_dictionary import get_full_word_list
import pickle

initial_word_list = np.array(get_full_word_list('wordle_dictionary.txt',5))

current_word_list = np.copy(initial_word_list)

def optimization(word_list, possibilities, use_log=True):
    expected_information = np.zeros(len(word_list))
    
    for w in range(len(word_list)):
        response_counts = dict()
        normalization_factor = 0
        for r in possibilities:
            response = wordle_solver.simulate_wordle_response(r, word_list[w])
            if response in response_counts:
                response_counts[response] += 1
            else:
                response_counts[response] = 1
            normalization_factor += 1

        probabilities = np.array(list(response_counts.values())) / normalization_factor
        if use_log:
            expected_information[w] = -1 * np.sum(probabilities * np.log2(probabilities))
        else:
            expected_information[w] = -1 * np.sum(probabilities**2)
    
    possibility_set = set(possibilities)
    
    for w in range(len(word_list)): #Boost possible words slightly to break ties as these give prob of premature victory
        if word_list[w] in possibility_set:
            expected_information[w] += 0.0001
                       
    r = np.argsort(-1 * expected_information)
    
    return (r, expected_information[r])


def solve(word_list, possibilities, word, use_log, first_guess, second_guesses):
    working_possibilities = np.copy(possibilities)
    guess = first_guess
    second_guess = True
    n_turns = 1
    while True:
        if guess == word:
            return n_turns
        response = wordle_solver.simulate_wordle_response(word,guess)
        working_possibilities = wordle_solver.update_word_list(working_possibilities,guess,response)
        if second_guess:
            if response in second_guesses:
                guess = second_guesses[response]
            else:
                suggestions, info_scores = optimization(word_list, working_possibilities, use_log=use_log)
                guess = word_list[suggestions[0]]
                second_guesses[response] = guess
            second_guess = False
        else:
            suggestions, info_scores = optimization(word_list, working_possibilities, use_log=use_log)
            guess = word_list[suggestions[0]]
        n_turns += 1
        
        
print("Computing first guess for log strategy...")
suggestions, info_scores = optimization(initial_word_list, current_word_list)
first_log_guess = initial_word_list[suggestions[0]]
print("First guess for log strategy is " + first_log_guess)
print("Computing first guess for absolute number strategy...")
suggestions, info_scores = optimization(initial_word_list, current_word_list,use_log=False)
first_absolute_guess = initial_word_list[suggestions[0]]
print("First guess for absolute number strategy is " + first_absolute_guess)

second_log_guesses = dict()
second_absolute_guesses = dict()

log_scores = []
absolute_number_scores = []
for word in tqdm(current_word_list):
    log_scores.append(solve(initial_word_list, current_word_list, word, True, first_log_guess, second_log_guesses))
    absolute_number_scores.append(solve(initial_word_list, current_word_list, word, False, first_absolute_guess, second_absolute_guesses))
    
print(np.mean(np.array(log_scores)))
print(np.mean(np.array(absolute_number_scores)))

pickle.dump(np.array(log_scores), open('log_scores.pkl','wb'))
pickle.dump(np.array(absolute_number_scores), open('absolute_number_scores.pkl','wb'))
        