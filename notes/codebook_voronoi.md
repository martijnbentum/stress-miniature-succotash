The structure of the codebook over pretraining visualized with a voronoi plot based on cosine similarity distance matrix 

update show split of the two codebooks,

left side (four plots) show phoneme t, and right side (four plots) show phoneme 'ə' (two most frequent phonemes in dutch)

(per side)
the upper plots show codebook 1 & 2 the lower plots show the location of the codevectors of both codebook in a single space

for the upper plot the color intensity shows the number of times a codevector occurs for a phoneme
lower left side shows spatial distribution of codevectors for codebook 1 in blue and codebook 2 in red
lower right side color intensity shows the number of times a codevector occurs for a phoneme for both codebooks in one similarity space

Checkpoint training Step 100

<img width="1806" alt="voronoi_step_100" src="https://github.com/user-attachments/assets/d8b442bf-00d0-4c77-beef-e035060ee572" />

Checkpoint training Step 1000

<img width="1765" alt="voronoi_step_1000" src="https://github.com/user-attachments/assets/45604b9e-81e7-48de-9917-827f75645046" />

Checkpoint training Step 10000

<img width="1781" alt="voronoi_step_10_000" src="https://github.com/user-attachments/assets/1d4d765c-afc5-4efc-a038-1cc56fd078c9" />

Checkpoint training Step 100000

<img width="1820" alt="voronoi_step_100_000" src="https://github.com/user-attachments/assets/b70fe8fb-879f-4e2c-9bad-21c8ced13cfd" />

older version (without splitting codebooks)

The polygons are colored according to the counts for the specific codevector based on phoneme /t/


Checkpoint training Step 100, many codevectors are used and codevectors polygons evenly distributed
<img width="775" alt="Screenshot 2025-04-25 at 17 34 33" src="https://github.com/user-attachments/assets/35c5312a-1094-4066-a859-e534ee8ff82a" />

Checkpoint training Step 1000, some codevectors are not used
<img width="777" alt="Screenshot 2025-04-25 at 17 34 40" src="https://github.com/user-attachments/assets/f0c8cf3c-804c-415e-9176-3f75da40962e" />

Checkpoint training Step 5000, most codevectors are not used
<img width="774" alt="Screenshot 2025-04-25 at 17 34 46" src="https://github.com/user-attachments/assets/3bfd58ee-8b61-4858-9cf3-efae3711fbac" />

Checkpoint training Step 10000, some codevectors are used some of the time mor adjecent codevector usage, maybe different sized polygons
<img width="780" alt="Screenshot 2025-04-25 at 17 34 55" src="https://github.com/user-attachments/assets/2af11b2d-0e53-4d0a-aeec-3943d16209c1" />

Checkpoint training Step 50000, range of frequency of use and many adjacent, middle polygons are smaller and mostly unused
<img width="788" alt="Screenshot 2025-04-25 at 17 35 02" src="https://github.com/user-attachments/assets/81570db6-96cb-4d4d-9665-5865bca868f3" />

Checkpoint training Step 100000, range of frequency of use and many adjacent ( but less smooth than at 50K) middle polygons are even smaller
<img width="788" alt="Screenshot 2025-04-25 at 17 35 08" src="https://github.com/user-attachments/assets/d0dff7ed-952e-4a44-958b-799a9f6f34a8" />



/ə/

Checkpoint training Step 100
<img width="786" alt="Screenshot 2025-04-25 at 17 52 29" src="https://github.com/user-attachments/assets/dd7c3227-bd1b-4928-8849-e00d0956dca3" />

Checkpoint training Step 1000
<img width="784" alt="Screenshot 2025-04-25 at 17 52 23" src="https://github.com/user-attachments/assets/f7c3a1b2-8690-4994-82b0-e6c14b1c2578" />

Checkpoint training Step 5000
<img width="774" alt="Screenshot 2025-04-25 at 17 52 17" src="https://github.com/user-attachments/assets/4751bb91-4e33-4c20-a28b-35bb9b4faf77" />

Checkpoint training Step 10000
<img width="780" alt="Screenshot 2025-04-25 at 17 52 11" src="https://github.com/user-attachments/assets/a966b232-ee10-46be-ac98-3a98509de563" />

Checkpoint training Step 50000
<img width="780" alt="Screenshot 2025-04-25 at 17 52 04" src="https://github.com/user-attachments/assets/60a68266-c22d-4c28-83e0-40eb841b0729" />

Checkpoint training Step 100000
<img width="782" alt="Screenshot 2025-04-25 at 17 51 58" src="https://github.com/user-attachments/assets/80009bc3-3133-499c-87e6-c73f3821963f" />


