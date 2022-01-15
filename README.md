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

At this point you may be wondering why taking the logarithm makes any difference at all. The logarithm is an increasing function (if a < b then log(a) < log(b)), so if we try to minimize the number of remaining words after our guess, shouldn't that be the same as trying to minimize the logarithm of the number of words remaining?

Surprisingly, it's not the same, and it's because of what happens when we take the average. Take the table above. What has the higher average? The first and last rows taken together, or the middle 4 rows? If you look at the left hand column, you'd say that the first and last rows have the higher average (33 vs 15). If you look at the right hand column, you'd say that the average of the two groups is equal (3.5). This shows that minimizing the average of n is not the same optimization problem as minimizing the average of log(n). It won't be completely different, 'kudzu' will come out as a bad word under both strategies, but it will be different.

So why is minimizing the average of log(n) the right thing to do, rather than just minimizing n? It helps to remember what we ultimately care about here. Is our ultimate goal actually to minimize the number of remaining words? No. Our goal is to finish the game in the fewest number of turns. But we should expect the number of turns required to be roughly proportional to the the logarithm of the number of possible words. This justifies taking log(n) as the "cost function" in our optimization problem.

## Method 1: Letter-by-letter approximation

We've defined what we mean by the optimum guess, so all that remains is to compute it. If we think about it, this seems like a daunting problem. We need to calculate what the average outcome of every possible guess would be. That means we need to consider every possible guess we could make (there's about 10,000 words in Wordle's valid word list), and for each of those, we then need to consider every possible solution to the game (on guess 1 this is again about 10,000). That's 100,000,000 Wordle goes that we'd need to simulate in order to work out the best guess for the first move. Not impossible (and we'll get to that in method 2), but it would be nice to have a quicker method to start off with, especially if we end up generalising this to the Wordle unlimited game, which allows different word lengths.

The approach we'll take first is to focus on individual letters at a time. If we could work out how valuable each of the 26 letters is in position 1, and how valuable each letter is in position 2, etc, then to evaluate how good a particular word might be, we could simply sum the values of its letters. Once we've evaluated every possible word in this way, we can work out what the best one is to use as our guess. This will only be an approximation to the correct answer, and we will discuss some of its limitations below, but it will actually turn out to agree with Method 2 on the best starting guess: "tares". And we can compute Method 1 in a fraction of a second while Method 2 takes 20 minutes.

How do we compute the value of an individual letter? The same way we would calculate the value of a whole word.

Suppose we want to evaluate how valuable the letter 'a' is to have in position 1. Placing the letter 'a' in position 1 can have 3 possible outcomes: it could turn green, orange or grey. These outcomes partition the set of possible words into 3, depending on which outcome they are consistent with. For example, of the ~12,000 words in Wordle's valid word list, suppose 1,000 would be consistent with the green outcome (i.e. they start with an 'a'), 5,000 would be consistent with the orange outcome (i.e. they contain an 'a' but it's not the first letter), and 6,000 would be consistent with the grey outcome (i.e. they contain no 'a's) (these numbers have all been made up for this example).

Just like with the words, we want to minimize the expected logarithm of the number of words that will remain once we have been told the outcome of our guess (and here we are only considering the information we get from the letter 'a' in position 1). What would that be in this made up example? Well, assuming all valid words are equally likely to be the answer, there's a 1,000/12,000 chance that we would be left with 1,000 options, a 5,000/12,000 chance that we would be left with 5,000 options, and a 6,000/12,000 chance that we would be left with 6,000 options. If we denote the three probabilities by p_1, p_2, p_3, and the total size of the word list by N, then the general formula is going to be given by:

<img src="https://render.githubusercontent.com/render/math?math=\sum_{i} p_{i} \log(p_{i} N)">

This is the quantity we want to minimize. If we compute its value for letter a in position 1, we can use that as a 'score' for letter a in position 1. If we repeat this for every letter in every position, we can then compute the score for any word by summing the scores of its letters. The best word will be the one with the lowest score.

We can actually simplify this formula a bit. It follows from the basic properties of logarithms that:

<img src="https://render.githubusercontent.com/render/math?math=\log(p_{i} N) = \log(p_{i})%2B\log(N)">

And <img src="https://render.githubusercontent.com/render/math?math=\log(N)"> is constant. So minimizing this cost function is equivalent to minimizing:

<img src="https://render.githubusercontent.com/render/math?math=\sum_{i} p_{i} \log p_{i}">

And this is equivalent to *maximizing*:

<img src="https://render.githubusercontent.com/render/math?math=-\sum_{i} p_{i} \log{p_{i}}">

This formula is famous! If you calculate this for any probability distribution it will tell you the *Shannon entropy*. And that is supposed to tell you the amount of information you will receive if you take a single sample from the distribution. And that is exactly what we've now shown it is! We've so far been thinking in terms of minimizing the amount of information that will still be missing after we've made our guess, but we can take the opposite point of view and talk about maximizing the amount of information that the outcome of the guess will give us. That's what the Shannon formula does. It is equal to 0 whenever the outcome is certain, and it is maximized when all outcomes are equally likely.

In summary, for each letter, in each of the 5 positions, we can compute the Shannon entropy, which is the amount of information that using that letter in that position can be expected to give us, on average. We can calculate this from the probabilities of each of the 3 possible outcomes (green/orange/grey) using the formula above. The best letters in each position will be the ones which partition the set of words into 3 similar sized groups, consistent with each respective outcome. The worst letters are those which are almost certain to give a particular outcome (e.g. 'x' will almost certainly be grey and so is a bad choice).

We can perform this computation relatively quickly. We just need to make one pass through the word list to sum up the number of occurrences of green/orange/grey for each letter in each position. That's then enough to give us all the probabilities we need. After that we need one more pass through the word list to sum up the value of each word using the value of its letters. So we only need to do 2 loops through the ~10,000 words, instead of the ~10,000 loops through the ~10,000 words that are needed under Method 2.

We said this method was just an approximation to the correct answer, so what's wrong with it? What does it miss? The big assumption we are making with this approach is that each letter is independent. This is obviously not true. For example, suppose we use a letter 'Q' in position 1. That should reduce the information provided by a 'U' in position 2, because in all the cases where the 'Q' comes back green, position 2 must be a letter 'U' with probability 1. Method 1 can't capture that kind of interaction, and so may slightly overestimate the value of a word starting 'QU...'.

More seriously, this approach is going to go very wrong when it comes to guesses that contain double letters. If we try a guess with 2 'L's, then we know that we will *never* have the second 'L' turn orange with the first 'L' turning grey (the game only highlights the first match). And it is very unlikely to turn orange even if the first 'L' turns orange or green (that would only happen if there are at least 2 'L's in the answer and the second 'L' is in the wrong place). So in this case, using a 'L' in your guess dramatically reduces the information content of all subsequent 'L's. The method we've described so far, which just sums up the values of the letters, doesn't capture that effect. Indeed, if I try to implement the method described so far, the top suggested guesses all have repeated letters, which clashes with the intuition that it would be better to try as many different letters as possible on your first guess in order to get the most information.

To fix this problem, I've added a heuristic fudge to method 1 which discounts the value of repeated letters. When evaluating the value of a letter in a particular place in a particular word, if that letter has already occurred in the guess, I pretend that the probability of an orange is now 0, and make up for that reduction in probability with an increased probability of grey (the probability of a green is unchanged, since this really is independent of the other letters in the guess). This fudge actually works surprisingly well, because the top suggested guess from Method 1 is then "tares", which agrees with the top suggested guess of the more accurate, but slower, Method 2.

## Method 2: Finding the optimum guess without any approximations

Under Method 1 we approximated the value of a word by summing the value of its letters. We saw that that worked pretty well, but it's not guaranteed to give us the right answer. It allowed for the same letter to have different values in different positions, but it didn't allow for interactions between the different letters (e.g. the fact that a 'Q' affects the information content of a following 'U'). We now want to compute the value of a word exactly, by considering it as a whole, taking absolutely everything into consideration.

The only formula we need in order to evaluate the value of a particular word is the Shannon entropy formula that we already derived:

<img src="https://render.githubusercontent.com/render/math?math=-\sum_{i} p_{i} \log{p_{i}}">

But now instead of the probabilities corresponding to the chances of green/orange/grey for each letter, they will correspond to the chances of *every possible 5 symbol response* that we might get to our entire guess. In principle, for each guess, there might be as many as 3^5 = 243 different possible outcomes, all with different likelihoods. In practice, some of these outcomes might be impossible given the remaining word list.

The full procedure for evaluating the value of a particular guess, X, is the following:

- Loop through the entire list of remaining possible solutions and compute what the Wordle response would be if guess X was made against that solution.
- Sum up how many times each different Wordle response occurs for guess X, and use that to compute the *probability* of each response happening after guess X is made.
- Apply the Shannon formula to these probabilities, to calculate the expected amount of information that making guess X will give us.

Once we have followed this procedure for every possible guess, X, we can then pick the X with the largest information content to use as our next guess.

The number of possible guesses we could make is the same on each turn, because we are allowed to guess words that have already been ruled out, and in fact it will often be beneficial to do this if they will give us more information. The number of possible solutions is reduced dramatically on each turn though, which makes the Method 2 computation more and more feasible as the game progresses.

The first turn is the only turn on which Method 2 runs prohibitibely slowly. It takes about 20 minutes to complete on my machine, which is longer than you probably want to spend on a game of Wordle. But fortunately, the computation for Guess 1 is exactly the same each time, so you only need to run it once, cache the results, and retrieve those results in subsequent games.
