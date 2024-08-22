## Overview of the acoustic correlates of stress for Dutch, German and English

### Words with exactly two syllables (Dutch, German and English)
Intensity, duration, formant peripherality, pitch, spectral tilt (used LDA to compute a single value) and all acoustic features combined.

Stressed syllables are typically louder (higher intensity), have a longer duration, the formants F1 & F2 are more peripheral, have a shallower spectral tilt. The distributions of stressed and unstressed vowel shown below for Dutch, German and English show tendencies in the expected directions

| Language | Stress Type  |   Count  |
|----------|--------------|----------|
| Dutch    | Stress       |   160,692|
| Dutch    | No Stress    |   185,498|
| German   | Stress       |   373,553|
| German   | No Stress    |   675,786|
| English  | Stress       |   555,360|
| English  | No Stress    |   781,921|


<img width="1888" alt="Screenshot 2024-08-12 at 11 54 15" src="https://github.com/user-attachments/assets/9f5b2d48-c9f8-467f-8fe8-9592851a710c">


### Classifier performance based on acoustic correlates of stress and wav2vec 2 embeddings

<img width="1861" alt="Screenshot 2024-08-22 at 11 26 18" src="https://github.com/user-attachments/assets/49b0d9db-ff86-4e60-bc56-acd963c1f202">



### All syllables (Dutch, German and English)

Intensity, duration, formant peripherality, pitch, spectral tilt (used LDA to compute a single value) and all acoustic features combined.

Stressed syllables are typically louder (higher intensity), have a longer duration, the formants F1 & F2 are more peripheral, have a shallower spectral tilt. The distributions of stressed and unstressed vowel shown below for Dutch, German and English show tendencies in the expected directions. We selected all words (1 syllable or more) and every word is assumed to have one stressed syllable also if it is monosyllabic and has sjwa for a vowel e.g. de or het in Dutch.

| Language | Stress Type  |      Count |
|----------|--------------|-----------:|
| Dutch    | Stress       |     714,974 |
| Dutch    | No Stress    |     578,706 |
| German   | Stress       |   1,739,883 |
| German   | No Stress    |   1,814,216 |
| English  | Stress       |   3,350,290 |
| English  | No Stress    |   1,510,532 |


![Screenshot 2024-08-08 at 15 58 07](https://github.com/user-attachments/assets/bdb1ad56-e31a-4efc-844c-3e1051229f0f)
