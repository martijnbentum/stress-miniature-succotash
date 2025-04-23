Codevector distribution during training. I applied the Dutch model checkpoints to a subset (~ 5 hours / 1,792,704 frames) of CGN read aloud books (comp-o). The first 10k steps seem to be important for structuring the codebook.
I collected the codevector indices for all 1.7M frames (2 indices per frame) and then counted how many times each individual index occurs.
Entropy: entropy over the distribution of codevectors
Max count: count of the most frequent codevector
Min count: count of the least frequent (non zero) codevector
Unique count: number of occurring codevectors (150 - 640) out of 640


<img width="773" alt="Screenshot 2025-04-23 at 12 19 55" src="https://github.com/user-attachments/assets/1bcb8207-bccd-43f1-a564-d25fc5b791ce" />

<img width="780" alt="Screenshot 2025-04-23 at 12 20 43" src="https://github.com/user-attachments/assets/7f1cef36-0042-47b1-887c-6f6fa6c250cd" />

Codevector evolution over training

codevector more frequently used in later checkpoints
<img width="864" alt="Screenshot 2025-04-23 at 13 04 47" src="https://github.com/user-attachments/assets/fbfe414a-cb1b-4e34-bded-70f09994363c" />

codevector less frequently used in later checkpoints
<img width="854" alt="Screenshot 2025-04-23 at 13 06 50" src="https://github.com/user-attachments/assets/64dbd0dc-2054-4ce6-8b98-43bb62761db3" />

codevector not used in later check points 0 usage after checkpoint 2000 (on clean read aloud speech)
<img width="855" alt="Screenshot 2025-04-23 at 13 16 27" src="https://github.com/user-attachments/assets/c55561e3-bbd0-4f17-a86a-deb73fa1de66" />
