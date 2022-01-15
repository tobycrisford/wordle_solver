- A python script to help solve the Wordle game: clone and run wordle_solver.py to use.
- A "debrief" app to give you interesting stats on your guesses after finishing a wordle game. Go here to use: https://share.streamlit.io/tobycrisford/wordle_solver/main/wordle_debrief_app.py

# Solving Wordle with a Computer

The game Wordle has recently (Jan 2021) gone viral. If you've not seen it before, you can play here: https://www.powerlanguage.co.uk/wordle/. The aim is to discover an unknown 5 letter word by making repeated guesses (with a maximum 6 guesses allowed). In response to each guess, you are told which letters you got in the right position (highlighted green), which letters are present in the word but you put in the wrong position (highlighted orange), and which letters are not present in the word at all (highlighted grey). It's a simple but addictive game.

Can a computer help us to play Wordle? Of course. If the computer knows the list of possible words, then it can automatically whittle down this list as you receive the response to each guess, letting you know which words are left, until only one possible word remains. It's fairly straightforward to get a computer to do that. The more interesting question is: **Can the computer tell us the optimum word to guess next at each stage?**

This repository contains a python script for doing just that, which makes use of information theory to calculate the optimum guess. There are three different methods it can use to do this (you can select which one you would like to use at each stage when you run the script):

- The first is an approximate heuristic method, but it can run instantly.
- The second method uses a brute force search to return the optimum guess, under the assumption that all valid guesses are equally likely to be correct. This takes about 20 minutes to run on my computer to return the first guess, but runs in under 30 seconds after that. Fortunately the best first guess is the same every time (it's "tares") so you don't have to run the brute force search on the first guess every time you play.
- The third method expands on the second method by taking into account how often each word appears in typical English text. It is based on the observation that more common words are more likely to appear as answers to the Wordle game (no one wants the answer to be a word they had never heard of).

The rest of this readme explains in detail how each of these three methods work, introducing concepts from information theory as they are needed.

## What are we trying to do?

Before we can program a computer to tell us the optimum word to guess next, we have to define what 'optimum word' means. Wordle players already have an intuitive sense of this. Putting common letters in your word seems like a good idea, and putting rare letters seems like a bad idea. Why? Because if you try a word like 'kudzu' on your first go, then most of the time you will receive back 5 greys, and the list of remaining words you still need to eliminate will be very long. Sure, sometimes you might get lucky. If the 'z' came back green or orange then you'd be almost there! But *on average*, this guess is going to leave you with many more remaining options to eliminate than a word like 'tares' would.

This suggests a way to define the optimum guess: The optimum guess is the one which minimizes the *expected* number of possible words that will remain after we are told the result of the guess.

The word 'expected' in this definition is really just a mathematical way of saying 'on average'.

But this definition isn't quite what we use here. Instead, we follow information theorists in defining our optimum guess this way:

**The optimum guess is the one which minimizes the *expected* *logarithm* of the number of possible words that will remain after we are told the result of the guess.**

What does applying a logarithm to the number do? In the table below I've listed some possible sizes of the set of remaining words in the left hand column, and what you'd get by applying the logarithm (in base 2) in the right hand column.

| Size of set, n  | log(n) |
| ------------- | ------------- |
| 2  | 1  |
| 4  | 2  |
| 8 | 3 |
| 16 | 4 |
| 32 | 5 |
| 64 | 6 |

Here's an intuitive way to think about what applying the logarithm tells you. Imagine you want to uniquely label every word in your set using "bits". Bits are symbols that can only take on two values: 0 or 1. The logarithm tells you how many bits of information you will need in order to uniquely label every word in the set. For example, if you have 4 words, then you need 2 bits: 00, 01, 10, 11. If you have 8 words, you need 3 bits: 000,001,010,011,100,101,110,111. If we try to minimize the logarithm of the number of words remaining after we've made our guess, then we are minimizing the amount of *information*, measured in *bits*, that we will still be missing.

At this point you may be wondering why taking the logarithm makes any difference at all. The logarithm is an increasing function (if a < b then log(a) < log(b)), so if we try to minimize the number of remaining words after our guess, n, shouldn't that be the same as trying to minimize the logarithm of the number of words remaining, log(n)?

Surprisingly, it's not the same, and it's because of what happens when we take the average. Take the table above. What has the higher average? The first and last rows taken together, or the middle 4 rows? If you look at the left hand column, you'd say that the first and last rows have the higher average (33 vs 15). If you look at the right hand column, you'd say that the average of the two groups is equal (3.5). This shows that minimizing the average of n is not the same optimization problem as minimizing the average of log(n). It won't be completely different, 'kudzu' will come out as a bad word under both strategies, but it will be different.

So why is minimizing the average of log(n) the right thing to do, rather than just minimizing n? It helps to remember what we ultimately care about here. Is our ultimate goal actually to minimize the number of remaining words? No. Our goal is to finish the game in the fewest number of turns. But we should expect the number of turns required to be roughly proportional to the the logarithm of the number of possible words. This justifies taking log(n) as the "cost function" in our optimization problem.

## Method 1: Letter-by-letter approximation

We've defined what we mean by the optimum guess, so all that remains is to compute it. If we think about it, this seems like a daunting problem. We need to calculate what the average outcome of every possible guess would be. That means we need to consider every possible guess we could make (there's about 10,000 words in Wordle's valid word list), and for each of those, we then need to consider every possible solution to the game (on guess 1 this is again about 10,000). That's 100,000,000 Wordle goes that we'd need to simulate in order to work out the best guess for the first move. Not impossible (and we'll get to that in method 2), but it would be nice to have a quicker method to start off with, especially if we end up generalising this to the Wordle unlimited game, which allows different word lengths.

The approach we'll take first is to focus on individual letters at a time. If we could work out how valuable each of the 26 letters is in position 1, and how valuable each letter is in position 2, etc, then to evaluate how good a particular word might be, we could simply sum the values of its letters. Once we've evaluated every possible word in this way, we can work out what the best one is to use as our guess. This will only be an approximation to the correct answer, and we will discuss some of its limitations below, but it will actually turn out to agree with Method 2 on the best starting guess: "tares". And we can compute Method 1 in a fraction of a second while Method 2 takes 20 minutes.

How do we compute the value of an individual letter? The same way we would calculate the value of a whole word. A single letter in a single position has 3 possible results: green, orange, or grey. We would like a letter which will, on average, leave the smallest (log of the) number of remaining words once we are told its result...
