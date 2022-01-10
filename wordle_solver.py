# -*- coding: utf-8 -*-
"""
Created on Mon Jan 10

@author: tobycrisford
"""

import numpy as np
from english_words import english_words_set
from tqdm import tqdm

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
                    information[w] += - p * np.log(p)
                    
    r = np.argsort(-1 * information)
    
    return (r, information[r])


def simulate_wordle_response(word, guess):
    
    response = ['-' for i in range(len(guess))]
    wlist = [c for c in word]
    glist = [c for c in guess]
    
    for l in range(len(guess)):
        if word[l] == guess[l]:
            response[l] = '*'
            wlist[l] = '^'
            glist[l] = '_'
            
    for i in range(len(guess)):
        for j in range(len(word)):
            if glist[i] == wlist[j]:
                response[i] = '.'
                wlist[j] = '^'
                glist[i] = '_'
                break
    
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


# Just to see if this would work
def get_suggestions_brute_force(word_list, possibilities):
    
    expected_next_count = np.zeros(len(word_list))
    
    for w in tqdm(range(len(word_list))):
        for possible in possibilities:
            response = simulate_wordle_response(possible, word_list[w])
            for nested_possible in possibilities:
                if simulate_wordle_response(nested_possible, word_list[w]) == response:
                    expected_next_count[w] += 1
        expected_next_count[w] /= len(possibilities)
    
    r = np.argsort(expected_next_count)
    
    return (r, expected_next_count[r])

#Can clearly speed the brute force method up a lot while keeping basic structure
def get_suggestions_brutish_force(word_list, possibilities):
    
    expected_next_count = np.zeros(len(word_list))
    
    for w in tqdm(range(len(word_list))):
        response_dict = dict()
        for possible in possibilities:
            response_dict[possible] = simulate_wordle_response(possible, word_list[w])
        response_counts = dict()
        for r in response_dict:
            if response_dict[r] in response_counts:
                response_counts[response_dict[r]] += 1
            else:
                response_counts[response_dict[r]] = 1
        expected_next_count[w] = np.sum(np.array(list(response_counts.values()))**2) / len(possibilities)
    
    possibility_set = set(possibilities)
    
    for w in range(len(word_list)): #Boost possible words slightly to break ties as these give prob of premature victory
        if word_list[w] in possibility_set:
            expected_next_count[w] -= 0.0001
            
    r = np.argsort(expected_next_count)
    
    return (r, expected_next_count[r])
        

initial_word_list = np.array([w for w in english_words_set if len(w) == 5 and w.lower() == w])

current_word_list = np.copy(initial_word_list)

while True:
    
    (green_counts, orange_counts) = create_counts(current_word_list)
    brute_force_q = input("Use brute force? (y/n):")
    use_brute_force = brute_force_q == 'y'
    if use_brute_force:
        suggestions, info_scores = get_suggestions_brutish_force(initial_word_list, current_word_list)
        print("Top suggested guesses:")
        print(initial_word_list[suggestions][0:5])
        print(info_scores[0:5])
        print(len(current_word_list))
    else:
        suggestions, info_scores = get_suggestions(current_word_list, green_counts, orange_counts)
        print("Top suggested guesses:")
        print(current_word_list[suggestions][0:5])
        print(info_scores[0:5])
        print(len(current_word_list))
    #other_suggestions, other_scores = get_suggestions(initial_word_list, green_counts, orange_counts)
    #print(initial_word_list[other_suggestions][0:5])
    #print(other_scores[0:5])
    next_guess = input("Enter your guess here:")
    result = input("Enter the result here, -=grey, .=orange, *=green:")
    current_word_list = update_word_list(current_word_list, next_guess, result)
    if len(current_word_list) == 1:
        print("I think I know the word: " + current_word_list[0])
        break