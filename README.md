# Wordle solver
Python script for solving the Wordle game.

Version 1: A hastily put together script for solving the Wordle game. The interesting bit is how to choose the next guess. This script tries to pick the word which will maximize the information received, using a heuristic method that treats each letter as independent (an exhaustive search seems unnecessarily complex). I realised this assumption might be particularly bad in the case of information from orange squares on repeated letters, so added a fudge to try to correct for this a bit. Also added facility to guess words which have 0 probability of being right if they add a lot of information, but this doesn't seem to help much in practice. End result seems to work pretty well.

Version 2: Tried the brute force search to see what would happen. It was going to take over 24 hours to run for the guess 1 suggestions (the code can probably be made much more efficient), but actually runs in reasonable time after guess 1! Code now changed so you can make use of the brute force strategy after your initial guess and play in a mathematically optimum way from that point on.

Version 3: Missed some obvious optimisations to the brute force approach. Now brute force is quick enough to be run from the first guess. Also changed it to minimize the expected value of the *log* of the remaining options after your guess, rather than the expected number of remaining options. I think this is the correct information theory thing to do. The log of the number of remaining words is going to be a better measure of the number of additional guesses required.

For those who are interested, the best first guess according to my dictionary (now updated to use the same word list as Wordle) seems to be 'tares', so now you know.
