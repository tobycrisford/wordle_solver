# -*- coding: utf-8 -*-
"""
Created on Sun Jan 16 17:04:35 2022

@author: tobycrisford

This script computes the best first guess for a "two or die" strategy,
using standard Wordle list.

For this, we assume that the top 10th percentile of words are equally likely to
be the answer, that the rest are impossible, and maximize our chances of getting
the correct answer on the second guess under this assumption.

The result is "tears"
"""

from wordle_dictionary import get_full_word_list
from tqdm import tqdm
import wordle_solver
import numpy as np

initial_word_list = np.array(get_full_word_list("wordle_dictionary.txt",5))

frequency_file = "wordle_dictionary.txt.5.pkl"
frequency_dict = wordle_solver.preprocess_word_frequencies(frequency_file, initial_word_list)

expected_next_guess_success = np.zeros(len(initial_word_list))

frequency_threshold = np.percentile(list(frequency_dict.values()), 90)

for w in tqdm(range(len(initial_word_list))):
    max_weight = dict()
    total_weight = dict()
    normalization_factor = 0
    
    for solution in initial_word_list:
        response = wordle_solver.simulate_wordle_response(solution, initial_word_list[w])
        if frequency_dict[solution] > frequency_threshold:
            rescaled_freq = 1
        else:
            rescaled_freq = 0
        if response in max_weight:
            if rescaled_freq > max_weight[response]:
                max_weight[response] = rescaled_freq
        else:
            max_weight[response] = rescaled_freq
        if response in total_weight:
            total_weight[response] += rescaled_freq
        else:
            total_weight[response] = rescaled_freq
        normalization_factor += rescaled_freq
    
    for response in max_weight:
        #expected_next_guess_success[w] += ((total_weight[response] / normalization_factor) * (max_weight[response] / total_weight[response]))
        #Interestingly above commented out formula independent of total_weight values, so can simplify:
        expected_next_guess_success[w] += (max_weight[response] / normalization_factor)
        
ind_order = np.argsort(-1 * expected_next_guess_success)

print(initial_word_list[ind_order[0:5]])
print(expected_next_guess_success[ind_order[0:5]])