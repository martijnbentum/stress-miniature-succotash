The structure of the codebook over pretraining visualized with a voronoi plot based on cosine similarity distance matrix 

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
