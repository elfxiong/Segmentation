# subsequence
from collections import defaultdict
from itertools import chain, combinations


def LCS(X, Y):
    """
    First finds a table (matrix) such that L[j][k] is length of longest common subsequence for X[0:j] and Y[0:k].
    Then, uses tracebacks through this table to print the actual LCS.
    This only works for two strings, and is the most straightforward dynamic programming solution,
    but it likely isn't the fastest.
    """
    n, m = len(X), len(Y)
    L = [[0] * (m + 1) for k in range(n + 1)]  # Creates matrix of values to fill
    for j in range(n):  # Loop through indices of 1st string
        for k in range(m):  # Loop through indices of 2nd str each time you're on an index of first
            if X[j] == Y[k]:  # If the characters match,
                L[j + 1][k + 1] = L[j][k] + 1  # fill in coordinates of table with value of upper left cell + 1.
            else:  # Otherwise,
                L[j + 1][k + 1] = max(L[j][k + 1], L[j + 1][k])  # choose max value from left cell or above cell
    solution = []  # Initialize a list for storing the solution
    j, k = len(X), len(Y)  # Now, do a traceback through L, starting with the highest valued cell.
    while L[j][k] > 0:
        if X[j - 1] == Y[k - 1]:
            solution.append(X[j - 1])
            j -= 1
            k -= 1
        elif L[j - 1][k] > L[j][k - 1]:  # This and the next elif pick the highest value in a cell to
            j -= 1  # the left or above in L.
        elif L[j - 1][k] < L[j][k - 1]:
            k -= 1
        elif L[j - 1][k] == L[j][k - 1]:  # Original algorithm didn't adequately deal with case in which
            # cell to the left or above were equally good.
            if X[j - 2] == Y[k - 1] and X[j - 2] not in {"a", "e", "i", "o", "u"}:  # Bias toward consonants in stem.
                j -= 1  # Eventually, need to not hardcode the vowels!!
            elif X[j - 1] == Y[k - 2] and Y[k - 2] not in {"a", "e", "i", "o", "u"}:  # Bias toward consonants in stem.
                k -= 1  # Eventually, need to not hardcode the vowels!!
            else:  # Default directionality: Leftward in chart.
                k -= 1
        else:  # Default directionality: Leftward in chart.
            k -= 1
    return ''.join(reversed(solution))


def m_longest_common_subsequence_2(s):
    """An iterative method to compute MLCS"""

    # Correct me if I'm wrong but I think unsorted list is faster
    lst = list(s)

    lcs = lst[0]
    for string in lst[1:]:
        lcs = LCS(lcs, string)

    return lcs


def lcs_length(X, Y):
    m = len(X)
    n = len(Y)
    # An (m+1) times (n+1) matrix
    C = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if X[i - 1] == Y[j - 1]:
                C[i][j] = C[i - 1][j - 1] + 1
            else:
                C[i][j] = max(C[i][j - 1], C[i - 1][j])
    return C


def back_track_all(C, X, Y, i, j):
    if i == 0 or j == 0:
        return {""}
    elif X[i - 1] == Y[j - 1]:
        return set([Z + X[i - 1] for Z in back_track_all(C, X, Y, i - 1, j - 1)])
    else:
        R = set()
        if C[i][j - 1] >= C[i - 1][j]:
            R.update(back_track_all(C, X, Y, i, j - 1))
        if C[i - 1][j] >= C[i][j - 1]:
            R.update(back_track_all(C, X, Y, i - 1, j))
        return R


def all_lcs(X, Y):
    """find *all* longest common subsequence"""
    return back_track_all(lcs_length(X, Y), X, Y, len(X), len(Y))


def m_longest_common_subsequence_3(iterable):
    """Find longest common subsequence for all strings in the iterable"""
    lst = list(iterable)

    lcs = lst[0]
    for string in lst[1:]:
        lcs = all_lcs(lcs, string).pop()  # TODO select a LCS instead of popping the last one

    return lcs


# substring


def longest_common_substring(s1, s2):
    m = [[0] * (1 + len(s2)) for i in range(1 + len(s1))]
    longest, x_longest = 0, 0
    for x in range(1, 1 + len(s1)):
        for y in range(1, 1 + len(s2)):
            if s1[x - 1] == s2[y - 1]:
                m[x][y] = m[x - 1][y - 1] + 1
                if m[x][y] > longest:
                    longest = m[x][y]
                    x_longest = x
            else:
                m[x][y] = 0
    return s1[x_longest - longest: x_longest]


def m_longest_common_substring(it):
    lst = list(it)

    lcs = lst[0]
    for string in lst[1:]:
        lcs = longest_common_substring(lcs, string)

    return lcs


# other


def powerset(iterable):
    """powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"""
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))


def subtract(x, y):
    """x - y"""
    return [item for item in x if item not in y]
