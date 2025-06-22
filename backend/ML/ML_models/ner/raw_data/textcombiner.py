import os

with open("all_data.txt", "w", encoding="utf-8") as outfile:
    for fname in os.listdir("raw_data"):
        with open(f"raw_data/{fname}", "r", encoding="utf-8") as f:
            outfile.write(f.read() + "\n\n")
