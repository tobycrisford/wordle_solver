# -*- coding: utf-8 -*-
"""
Created on Tue Feb 22 19:42:00 2022

@author: tobycrisford
"""

from wordle_dictionary import get_full_word_list
import numpy as np
import wordle_solver
from tqdm import tqdm
import pandas as pd
from wordle_vis import create_vis

clues = ["richard"]

word_list = np.array(get_full_word_list("wordle_unlimited_dictionary.txt", len(clues[0])))

potential_responses = dict()
for clue in clues:
    responses = []
    for word in word_list:
        responses.append(wordle_solver.simulate_wordle_response(word, clue))
    potential_responses[clue] = np.array(responses)

potential_answers = {column: [] for column in ["word", "value"] + clues}
for i in tqdm(range(len(word_list))):
    word = word_list[i]
    candidate_words = np.full(len(word_list), True)
    for clue in clues:
        candidate_words = candidate_words & (potential_responses[clue] == potential_responses[clue][i])
    if np.sum(candidate_words) == 1:
        min_dash = 5
        for clue in clues:
            min_dash = min(min_dash, potential_responses[clue][i].count("-"))
        potential_answers["word"].append(word)
        potential_answers["value"].append(min_dash)
        for clue in clues:
            potential_answers[clue].append(potential_responses[clue][i])
        
potential_answers_df = pd.DataFrame(potential_answers).sort_values("value", ascending=False)
print("---")      
print(potential_answers_df.iloc[0:20])


def create_output(df_index, filename):
    
    row_to_use = potential_answers_df.loc[df_index]
    responses = []
    for clue in clues:
        responses.append(row_to_use[clue])
    create_vis(clues, responses, filename)