# Wordle solver
Python script for solving the Wordle game.

A hastily put together script for solving the Wordle game. The interesting bit is how to choose the next guess. This script tries to pick the word which will maximize the information received, using a heuristic method that treats each letter as independent (an exhaustive search seems unnecessarily complex). I realised this assumption might be particularly bad in the case of information from orange squares on repeated letters, so added a fudge to try to correct for this a bit. Also added facility to guess words which have 0 probability of being right if they add a lot of information, but this doesn't seem to help much in practice. End result seems to work pretty well.
