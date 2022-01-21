# -*- coding: utf-8 -*-
"""
Created on Mon Jan 10

@author: tobycrisford
"""

import numpy as np
from wordle_dictionary import get_full_word_list
from tqdm import tqdm
import os
import pickle

use_brute_force = False

def fetch_count(count_dict, letter):
    r = count_dict.get(letter)
    if r is None:
        return 0
    else:
        return r

def get_suggestions(word_list, green_counts, orange_counts):
    
    information = np.zeros(len(word_list))
    for w in range(len(word_list)):
        for l in range(len(word_list[w])):
            green_prob = fetch_count(green_counts[l], word_list[w][l])
            orange_prob = fetch_count(orange_counts[l], word_list[w][l])
            grey_prob = 1 - (green_prob + orange_prob)
            if word_list[w][l] in word_list[w][0:l]: #Heuristic to deal with repeated letters where independence assumption badly violated
                orange_prob = 0
                grey_prob = 1 - green_prob
            for p in (green_prob, orange_prob, grey_prob):
                if p != 0:
                    information[w] += - p * np.log2(p)
                    
    r = np.argsort(-1 * information)
    
    return (r, information[r])


def simulate_wordle_response(word, guess):
    
    response = ['-' for i in range(len(guess))]
    word_letters = dict()
    for letter in word:
        if letter in word_letters:
            word_letters[letter] += 1
        else:
            word_letters[letter] = 1
    guess_tracker = {i for i in range(len(guess))}
    
    for i in range(len(guess)):
        if guess[i] == word[i]:
            response[i] = '*'
            word_letters[guess[i]] -= 1
            guess_tracker.remove(i)
    
    for i in range(len(guess)): #Loop from left as leftmost letter turns orange
        if i in guess_tracker:
            if guess[i] in word_letters:
                if word_letters[guess[i]] > 0:
                    response[i] = '.'
                    word_letters[guess[i]] -= 1
    
    return ''.join(response)
    
        

def update_word_list(word_list, guess, result):
    
    to_keep = np.full(len(word_list), True)
    
    for w in range(len(word_list)):
        to_keep[w] = simulate_wordle_response(word_list[w], guess) == result
                    
    return word_list[to_keep]

def create_counts(word_list):
    
    word_length = len(word_list[0])
    green_counts = [dict() for i in range(word_length)]
    orange_counts = [dict() for i in range(word_length)]
    
    for word in word_list:
        
        unique_letters = set(word)
        for l in range(len(word)):
            if word[l] in green_counts[l]:
                green_counts[l][word[l]] += 1 / len(word_list)
            else:
                green_counts[l][word[l]] = 1 / len(word_list)
            for ul in unique_letters:
                if ul in orange_counts[l]:
                    orange_counts[l][ul] += 1 / len(word_list)
                else:
                    orange_counts[l][ul] = 1 / len(word_list)
            orange_counts[l][word[l]] += -1 / len(word_list) #Didn't want to count this position
            
    return (green_counts, orange_counts)

#Can clearly speed the brute force method up a lot while keeping basic structure
def get_suggestions_brutish_force(word_list, possibilities, frequency_dict):
    
    expected_information = np.zeros(len(word_list))
    
    for w in tqdm(range(len(word_list))):
        response_counts = dict()
        normalization_factor = 0
        for r in possibilities:
            response = simulate_wordle_response(r, word_list[w])
            if response in response_counts:
                response_counts[response] += frequency_dict[r]
            else:
                response_counts[response] = frequency_dict[r]
            normalization_factor += frequency_dict[r]

        probabilities = np.array(list(response_counts.values())) / normalization_factor
        expected_information[w] = -1 * np.sum(probabilities * np.log2(probabilities))
    
    possibility_set = set(possibilities)
    
    for w in range(len(word_list)): #Boost possible words slightly to break ties as these give prob of premature victory
        if word_list[w] in possibility_set:
            expected_information[w] += 0.0001
                       
    r = np.argsort(-1 * expected_information)
    
    return (r, expected_information[r])

def get_entropy_of_words_remaining(word_list, frequency_dict):
    probabilities = [0 for w in word_list] #Dont convert until numpy until later because need more precision
    normalization_factor = 0
    for w in range(len(word_list)):
        probabilities[w] += frequency_dict[word_list[w]]
        normalization_factor += frequency_dict[word_list[w]]
    probabilities = np.array([p / normalization_factor for p in probabilities])
    probabilities = probabilities[probabilities != 0] #Some tiny values get rounded to 0 by numpy so just filter them out
    return -1 * np.sum(probabilities * np.log2(probabilities))

def get_candidate_word_probs(word_list, frequency_dict):
    probabilities = [0 for w in word_list]
    normalization_factor = 0
    for w in range(len(word_list)):
        probabilities[w] += frequency_dict[word_list[w]]
        normalization_factor += frequency_dict[word_list[w]]
    probabilities = np.array([p / normalization_factor for p in probabilities])
    
    r = np.argsort(-1 * probabilities)
    
    return r, probabilities[r]

def preprocess_word_frequencies(freq_file, word_list):
    frequency_dict = pickle.load(open(freq_file,'rb'))
    freqs = frequency_dict.values()
    max_freq = max(freqs)
    min_freq = min(freqs)
    for w in frequency_dict:
        frequency_dict[w] = frequency_dict[w] / max_freq
    for w in word_list:
        if not (w in frequency_dict):
            frequency_dict[w] = min_freq / max_freq
            
    return frequency_dict


if __name__ == "__main__":

    list_options = {'wordle': 'wordle_dictionary.txt', 'unlimited': 'wordle_unlimited_dictionary.txt'}
    
    list_choice = input("Please specify which game you are playing, 'wordle' or 'unlimited'?")
    
    length_choice = input("Which length of word are you playing?:")
    
    initial_word_list = np.array(get_full_word_list(list_options[list_choice], int(length_choice)))
    
    current_word_list = np.copy(initial_word_list)
    
    frequency_file = list_options[list_choice] + "." + length_choice + ".pkl"
    use_word_frequencies = 'n'
    if os.path.exists(frequency_file):
        use_word_frequencies = input("Would you like to make use of word frequencies from google books?(y/n)")
    if use_word_frequencies == 'y':
        frequency_dict = preprocess_word_frequencies(frequency_file, initial_word_list)
    else:
        frequency_dict = dict()
        for w in initial_word_list:
           frequency_dict[w] = 1
    
    while True:
        
        (green_counts, orange_counts) = create_counts(current_word_list)
        brute_force_q = input("Use brute force? (y/n):")
        use_brute_force = brute_force_q == 'y'
        print("Remaining words:",len(current_word_list))
        print("Required information:",get_entropy_of_words_remaining(current_word_list,frequency_dict)," bits")
        if use_brute_force:
            suggestions, info_scores = get_suggestions_brutish_force(initial_word_list, current_word_list, frequency_dict)
            print("Top suggested guesses and expected information they will provide (in bits):")
            print(initial_word_list[suggestions][0:5])
            print(info_scores[0:5])
        else:
            suggestions, info_scores = get_suggestions(current_word_list, green_counts, orange_counts)
            print("Top suggested guesses:")
            print(current_word_list[suggestions][0:5])
            print("Expected information they will provide (in bits):")
            print(info_scores[0:5])
        if use_word_frequencies == 'y':
            candidate_words, probs = get_candidate_word_probs(current_word_list, frequency_dict)
            print("Top candidate words and their probabilities:")
            print(current_word_list[candidate_words[0:5]])
            print(probs[0:5])
        #other_suggestions, other_scores = get_suggestions(initial_word_list, green_counts, orange_counts)
        #print(initial_word_list[other_suggestions][0:5])
        #print(other_scores[0:5])
        next_guess = input("Enter your guess here:")
        result = input("Enter the result here, -=grey, .=orange, *=green:")
        current_word_list = update_word_list(current_word_list, next_guess, result)
        if len(current_word_list) == 1:
            print("I think I know the word: " + current_word_list[0])
            break