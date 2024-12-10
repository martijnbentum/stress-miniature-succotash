## Stress assignment comparison with wav2vec 2 based stress classifiers on vowels in words and pseudowords

We used word and pseudoword recordings from the Baldey [dataset](https://www.mpi.nl/publications/item1950056/baldey-database-auditory-lexical-decisions)
This dataset was created for a lexical decision experiment and the recordings contain Dutch words and pseudowords.
The items are spoken in isolation by a single female speaker of Dutch. 

We selected 300 words and 300 pseudowords from the Baldey dataset. All items were bisyllabic and the stressed syllable was manually annotated.
We applied the pre-trained xlr wav2vec 2 [model](https://huggingface.co/facebook/wav2vec2-xls-r-300m) on the items.
For each syllable of each item the hidden states for the vowels were extracted and averaged for the cnn output and transformer layers 5, 11, 17 & 23.

We applied layer specific (i.e. cnn, 5, 11, ...) stress classifiers we trained on Dutch Common voice materials and collected the results.

_Table 1, percentage of correctly assigned stress labels for words and pseudowords for different layers of the wav2vec 2 model_
| Wav2Vec 2 Layer | Words  | Pseudowords |
|-----------------|--------|-----------|
| cnn             | 76.14  | 77.67     |
| 5               | 82.52  | 86.83     |
| 11              | 93.63  | 95.33     |
| 17              | 91.67  | 92.5      |
| 23              | 89.05  | 88.83     |
