import re
from collections import defaultdict
from sys import argv

import numpy as np

GAP_COST = 4
MIS_COST = 2
MATCH_COST = 0
THRESHOLD = 200


def get_words(text):
    return re.findall(r'[A-ZÁÉÍÓÚÂÊÔÀÁÉÍÓÚÂÊÔÀ]?[a-záéíóúâêôàáéíóúâêôà\-]+[\s.!?,;]?\s', text)

def clean(w):
    endings = ('.', ',', '!', '?')

    w = w.lower().strip()
    for e in endings:
        w = w.strip(e)

    return w.strip()

def get_distance(s1, s2):
    size_y = len(s1) + 1
    size_x = len(s2) + 1

    M = np.zeros((size_x, size_y))

    M[0,] = np.arange(size_y) * GAP_COST
    M[:,0] = np.arange(size_x) * GAP_COST

    for i in range(1, size_x):
        for j in range(1, size_y):
            diag_cost = M[i-1,j-1]
            diag_cost += 0 if s1[j-1] == s2[i-1] else MIS_COST

            M[i,j] = min(diag_cost,
                         M[i-1, j] + GAP_COST,
                         M[i, j-1] + GAP_COST)

    return M[size_x-1, size_y-1]

# print(get_distance('TACATG', 'CTACCG'))

if len(argv) < 1:
    print('Incorrect usage! Usage: python3 spellchecker.py [file]')

content = open('corpus.txt').read()
words = get_words(content)
words = set(map(clean, words))

vocabulary_file = 'vocabulary.txt'
with open(vocabulary_file, 'w') as vocabulary:
    vocabulary.write('\n'.join(words))
print(f'Vocabulary saved to {vocabulary_file}!')

print(f'Costs: deletion = {GAP_COST}, substitution = {MIS_COST}')
counter = 0
print(f'\nFound {counter} errors until now! Checking...\r', end='')

minimum_distances = defaultdict(lambda: 2**32)
for line_check in open(argv[1]):
    for word_check in line_check.split():
        word_check = clean(word_check)

        if not word_check in words:
            distances = defaultdict(list)
            for word in words:
                distance = get_distance(word_check, word)

                if distance <= THRESHOLD and distance < minimum_distances[word_check]:
                    distances[word_check, distance].append(word)
                    minimum_distances[word_check] = distance
            else:
                counter += 1
                print(f'Found {counter} errors until now! Checking...\r', end='')
print()

no_good_suggestions = [word for word, distance in minimum_distances.items() if distance > THRESHOLD]

# Get only the smallests distances
distances = filter(lambda x: x[0][1] > 0 and x[0][1] == minimum_distances[x[0][0]], distances.items())

print('\nDone! Suggestions:')
for (wrong, distance), suggestions in distances:
    suggestions = ', '.join(suggestions)
    print(f'\t{wrong} -> {suggestions} (distance: {distance})')

print('\nNo good suggestions: ' + ', '.join(no_good_suggestions))


# print('minimum_distances', minimum_distances)