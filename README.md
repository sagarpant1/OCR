# Optical-Character-Recognition
• Designed an algorithm to input an image and outputs its content in the text format with an accuracy of ~85% depending on the salt using Hidden Markov Model. • The current implementation includes only English

Calculating the transition probability from reading the training file-
While reading the training file line by line, the algorithm reduces the noise by removing the POS tags and the punctuation mark with a following.(dot) 
with just the punctuation mark. Then it reads the line character by character and thus stores the count for each transition.
The algorithm maintains two dictionaries first one to store the count of transition from the previous character to the current character and the second one to store the count of transitions from the previous character to any character. This is further used to calculate the transition probability.

Calculating the emission probability-
This could b addressed in different ways:
1) Calculating the ratio of match/total character between the test and the train letters. This approach gives works fine for noise-less data but fails for data with a lot of noise.
2) Maximizing the hit/miss ratio. Hit count is calculated by counting the matches for each pixel such the character is an asterisk '*'. Miss count is calculated by counting the pixels which have different characters for test and train data. Space count to count the number of spaces in both the test and the
train image. If the number of space count is very large then it means that there's a space. Otherwise, find the character with the highest hit/miss ratio.

Calculating initial probability-
This is calculated while reading the train data. A dictionary is maintained to store the count of each character as the first character of the
sentence. This count is later divided by the total count of all characters which appear as the first character of the sentence to compute the probability.

Methods employed to achieve the desired output-

1)Simple Bayes- This was done by maximising the hit/miss ratio for each character in the test image. The entire image sequence was computed using the same approach and final sequence was printed. 

2)HMM Using VE- This was calculated by finding the probability of each character occurring as the first character of the sentence. The product of Emission probability and initial probability was computed for each character. This was further used while computing the probability of the second character. The probability of the second character was computed by multiplying the transition probability with the probability from the previous state and summing it over all the possible transitions
and then multiplying the emission probability. This product was maximized for each possible character occurrence at position 2 and so on.

3) HMM Using Viterbi- This was calculated by finding the probability of each character occurring as the first character of the sentence. The product of Emission probability and initial probability was computed for each character. This was further used while computing the probability of the second character. The probability of the second character was computed by multiplying the transition probability with the probability from the previous state and then multiplying it with the emission probability. This product was maximized for each possible character occurrence at position 2 and so on.
