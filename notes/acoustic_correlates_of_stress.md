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

<img width="627" alt="Screenshot 2024-12-13 at 16 28 06" src="https://github.com/user-attachments/assets/16d253ae-1ce9-4434-87b2-83a1c6ef0b4f" />

### Classifier performance on other language

#### Dutch classifiers on other languages

<img width="633" alt="Screenshot 2024-12-13 at 16 29 24" src="https://github.com/user-attachments/assets/b304ef5f-2b1f-49ee-9629-df2761729177" />

#### English classifiers on other languages

<img width="631" alt="Screenshot 2024-12-13 at 16 30 42" src="https://github.com/user-attachments/assets/0f80406a-1dcd-4665-8889-2aaa4ccdf305" />

#### German classifiers on other languages

<img width="630" alt="Screenshot 2024-12-13 at 16 31 59" src="https://github.com/user-attachments/assets/005efe26-c277-48f9-952d-08e016aaf51a" />

#### Polish classifiers on other languages

<img width="630" alt="Screenshot 2024-12-13 at 16 32 43" src="https://github.com/user-attachments/assets/6f555d6e-1112-439b-ba07-f99b99012e23" />

#### Hungarian classifiers on other languages

<img width="631" alt="Screenshot 2024-12-13 at 16 33 18" src="https://github.com/user-attachments/assets/bbd466da-e3fb-4a2d-a250-bf7c8b2c62aa" />

### Pretrained dutch Finetuned Dutch and test results on all other languages combined

<img width="628" alt="Screenshot 2024-12-13 at 16 35 12" src="https://github.com/user-attachments/assets/9e2f8dbe-bf07-4aa0-ab0d-cd9995a5c7c8" />



# OLD

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
