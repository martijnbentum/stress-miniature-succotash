## Overview of the acoustic correlates of stress for Dutch, German, English, Polish

### Words with exactly two syllables (Dutch, German and English)
Intensity, duration, formant peripherality, pitch, spectral tilt (used LDA to compute a single value) and all acoustic features combined.

Stressed syllables are typically louder (higher intensity), have a longer duration, the formants F1 & F2 are more peripheral, have a shallower spectral tilt. The distributions of stressed and unstressed vowel shown below for Dutch, German and English show tendencies in the expected directions

| Language | Stress Type  |   Count  |
|----------|--------------|----------|
| Dutch    | Stress       |   157,760|
| Dutch    | No Stress    |   157,760|
| German   | Stress       |   264,963|
| German   | No Stress    |   264,963|
| English  | Stress       |   523,453|
| English  | No Stress    |   523,453|
| Polish   | Stress       |   320,937|
| Polish   | No Stress    |   320,937|
| Hungarian| Stress       |   104,970|
| Hungarian| No Stress    |   104,970|


<img width="1903" alt="Screenshot 2024-08-30 at 12 29 32" src="https://github.com/user-attachments/assets/47e14311-a007-47fd-9811-ef44fc02ec80">


### Classifier performance based on acoustic correlates of stress and wav2vec 2 embeddings

<img width="1912" alt="Screenshot 2024-09-11 at 17 28 08" src="https://github.com/user-attachments/assets/398c75f6-55b6-4f6e-b677-1347447666ae">




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
