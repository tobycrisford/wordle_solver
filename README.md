A python script to help solve the Wordle game. Clone and run wordle_solver.py to use.

# Solving Wordle with a Computer

The game Wordle has recently (Jan 2021) gone viral. If you've not seen it before, you can play here: https://www.powerlanguage.co.uk/wordle/. The aim is to discover an unknown 5 letter word by making repeated guesses (with a maximum 6 guesses allowed). In response to each guess, you are told which letters you got in the right position (highlighted green), which letters are present in the word but you put in the wrong position (highlighted orange), and which letters are not present in the word at all (highlighted grey). It's a simple but addictive game.

Can a computer help us to play Wordle? Of course. If the computer knows the list of possible words, then it can automatically whittle down this list as you receive the response to each guess, letting you know which words are left, until only one possible word remains. It's fairly straightforward to get a computer to do that. The more interesting question is: **Can the computer tell us the optimum word to guess next at each stage?**

This repository contains a python script for doing just that, which makes use of **information theory** to calculate the optimum guess. There are three different methods it can use to do this (you can select which one you would like to use at each stage when you run the script). The first is an approximate heuristic method, but which can run instantly. The second method uses a brute force search to return the optimum guess, under the assumption that all valid guesses are equally likely to be correct. The third method expands on the second method by taking into account how often each word appears in typical English text. It is based on the observation that more common words are more likely to appear as answers to the Wordle game (no one wants the answer to be a word they had never heard of). The rest of this readme explains in detail how each of these three methods work, introducing concepts from information theory as they are needed.

## What are we trying to do?

Before we can program a computer to tell us the optimum word to guess next, we have to define what 'optimum word' means. Wordle players already have an intuitive sense of this. Putting common letters in your word seems like a good idea, and putting rare letters seems like a bad idea. Why? Because if you try a word like 'kudzu' on your first go, then most of the time you will receive back 5 greys, and the list of remaining words you still need to eliminate will be very long. Sure, sometimes you might get lucky. If the 'z' came back green or orange then you'd be almost there! But *on average*, this guess is going to leave you many more options remaining afterwards than a word like 'raise' would.

This suggests a way to define the optimum guess: The optimum guess is the one which minimizes the *expected* number of possible words that will remain after we are told the result of the guess.

The word 'expected' in this definition is really just a mathematical way of saying 'on average'.

But this definition isn't quite what we use here. Instead, we follow information theorists in defining our optimum guess this way:

**The optimum guess is the one which minimizes the *expected* *log* of the number of possible words that will remain after we are told the result of the guess.**
