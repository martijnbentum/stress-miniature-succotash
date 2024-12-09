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

<img width="629" alt="Screenshot 2024-12-09 at 10 04 58" src="https://github.com/user-attachments/assets/2131d02b-af00-4dd9-9a9d-a21770b69012">

### Classifier performance on other language

#### Dutch classifiers on other languages

<img width="631" alt="Screenshot 2024-12-09 at 10 04 46" src="https://github.com/user-attachments/assets/4170350a-6007-41d4-a3b4-1b0435e9e84d">

#### English classifiers on other languages

<img width="629" alt="Screenshot 2024-12-09 at 10 04 33" src="https://github.com/user-attachments/assets/c3a574e8-ba54-4abd-a302-03d2b5488d72">

#### German classifiers on other languages

<img width="630" alt="Screenshot 2024-12-09 at 10 04 17" src="https://github.com/user-attachments/assets/37ebbb10-af27-48a9-a5d3-f952046fded0">

#### Polish classifiers on other languages

<img width="631" alt="Screenshot 2024-12-09 at 10 04 04" src="https://github.com/user-attachments/assets/22e6916f-9390-49e3-95e6-41a847a1e48f">

#### Hungarian classifiers on other languages

<img width="632" alt="Screenshot 2024-12-09 at 10 03 50" src="https://github.com/user-attachments/assets/e171e4ca-3e38-43d0-a1fe-cc05fc095215">

### Pretrained dutch Finetuned Dutch and test results on all other languages combined

<img width="630" alt="Screenshot 2024-12-09 at 11 34 03" src="https://github.com/user-attachments/assets/a0ac4f0f-912a-4a83-bde5-19facdb2dcfd">



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
