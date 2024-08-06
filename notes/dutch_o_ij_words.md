## overview of dutch o and ij words 

Selected a set of words with the vowel o or ij

Extracted embeddings from the Wav2vec 2.0 model from the cnn output layer and transformer layer 11 and 21. The embeddings were averaged for all frames within the onset, vowel, rime, coda and syllable (word is also shown but all words are mono syllabic so is the same as syllable).

With t-SNE (t-distributed stochastic neighbor embedding) implemented in scikit-learn vizualized the embeddings. As recommended, first PCA (principle component analysis) also implemented in scikit-learn) was used to down sampled to 50 components. This was down sampled to 2 dimensions with t-SNE. The t-SNE algorithm downsamples in such a way that similar objects are appear close together.

### word list and counts (maximum is set at a 100 word tokens)

| Word | Count |
|------|-------|
| zijn | 100   |
| zon  | 70    |
| wijn | 34    |
| bol  | 24    |
| won  | 21    |
| rijk | 20    |
| bijl | 15    |
| pop  | 8     |
| pijp | 7     |
| rok  | 7     |



### Onset
<img width="1825" alt="Screenshot 2024-08-06 at 09 31 34" src="https://github.com/user-attachments/assets/42c04ea2-8e06-4218-aa0e-51abf9e034a4">

### Vowel
<img width="1747" alt="Screenshot 2024-08-06 at 09 31 47" src="https://github.com/user-attachments/assets/370bc2b3-ae16-458b-a17f-838524d5244f">

### Rime
<img width="1825" alt="Screenshot 2024-08-06 at 10 41 27" src="https://github.com/user-attachments/assets/59d5a3bc-cf35-4683-b44d-68d631d93376">

### Coda
<img width="1823" alt="Screenshot 2024-08-06 at 11 27 59" src="https://github.com/user-attachments/assets/2afa76ec-8235-4192-bd46-0b685af2f7c9">

### Syllable
<img width="1823" alt="Screenshot 2024-08-06 at 12 00 09" src="https://github.com/user-attachments/assets/d016be1e-71f4-4ac8-acef-5fbad26c2da7">

### Word
<img width="1817" alt="Screenshot 2024-08-05 at 16 37 33" src="https://github.com/user-attachments/assets/1847b852-e480-4367-9a3b-5350a0a17545">
