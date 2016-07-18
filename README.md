# Segmentation

Research on a generalized, language-independent segmentation system which:

1. Does not need any segmented data to train or function
2. Can capitalize on the pairing of (morphological form, UniMorph features), or, more generally, of an inflected word and its full meaning (both lexical and inflectional).

Basic concepts used:

1. Longest Common Subsequence (LCS)
2. Frequency filtering
...

We are starting with agglutinative languages, such as Turkish, since they are easier to segment than fusional languages.

There is no single program as the files here are code pieces as a result of experimentation on the way to the goal.

The code is hosted at [GitHub](https://github.com/elfxiong/Segmentation).
