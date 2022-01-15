# -*- coding: utf-8 -*-
"""
Created on Sat Jan 15 11:07:36 2022

@author: tobycrisford
"""

import streamlit as st
import wordle_solver
import numpy as np
from wordle_dictionary import get_full_word_list
import pickle
import pandas as pd

word_length = 5

st.title("Wordle Debrief App")

st.text("Calculations are based on the assumption that the prior likelihood of each\nvalid word being the answer is proportional to its frequency\nin normal English text (using Google books).")
st.text("There are 12,972 words in Wordle's valid guess list, but most of these are \nvery obscure, and answers do seem to be biased towards more common words.")

answer = st.text_input("Wordle answer")

guesses = []
for i in range(word_length):
    guesses.append(st.text_input("Your guess #" + str(i+1)))
    
@st.cache
def get_full_word_list_cache(s, n):
    return get_full_word_list(s, n)

@st.cache
def preprocess_word_frequencies_cache(s, l):
    return wordle_solver.preprocess_word_frequencies(s, l)
    
initial_word_list = np.array(get_full_word_list_cache("wordle_dictionary.txt", 5))
    
frequency_dict = preprocess_word_frequencies_cache("wordle_dictionary.txt.5.pkl", initial_word_list)

current_word_list = np.copy(initial_word_list)

first_guess_results = pickle.load(open("first_guess.pkl","rb"))
    
if st.button('Create debrief'):
    with st.spinner("Creating debrief..."):
        for guess in enumerate(guesses):
            if (guess[1] != '') and (not (guess[1] is None)):
                if guess[0] == 0:
                    results = first_guess_results
                else:
                    results = wordle_solver.get_suggestions_brutish_force(initial_word_list, current_word_list, frequency_dict)
                    results = [initial_word_list[results[0]], results[1]]
                st.subheader("Before Guess #" + str(guess[0]+1) + "...")
                st.text("There were " + str(len(current_word_list)) + " possible words remaining.")
                st.text("The estimated information you were missing was " + str(wordle_solver.get_entropy_of_words_remaining(current_word_list, frequency_dict)) + " bits.")
                st.text("The automated solver thought the top 5 guesses for maximizing your information\n would have been:")
                st.table(pd.DataFrame({'Word': results[0][0:5], 'Expected information gain in bits': results[1][0:5]}))
                st.text("The automated solver thought the most likely answers at this stage were:")
                candidate_words, probs = wordle_solver.get_candidate_word_probs(current_word_list, frequency_dict)
                st.table(pd.DataFrame({'Word': current_word_list[candidate_words[0:5]], 'Probability': probs[0:5]}))
                st.text("You guessed " + guess[1])
                guess_info = np.where(results[0] == guess[1])[0]
                guess_prob = np.where(current_word_list[candidate_words] == guess[1])[0]
                st.text("The computer estimated this guess would provide " + str(results[1][guess_info]) + " bits of information.")
                st.text("The computer estimated that this guess had a probability " + str(probs[guess_prob]) + " of \nbeing correct.")
                current_word_list = wordle_solver.update_word_list(current_word_list, guess[1], wordle_solver.simulate_wordle_response(answer, guess[1]))