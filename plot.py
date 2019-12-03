import pandas as pd
import matplotlib.pyplot as plt
import sys

INPUT = sys.argv[1]
OUTPUT = sys.argv[2]

fig, ax = plt.subplots(1)
df = pd.read_csv(INPUT, sep=' ', header=None)
df[3]=df[0].str.len()
f=df.plot(kind='scatter', y=2, x=3, c=1, ax = ax)
ax.set_xlabel('length')
ax.set_ylabel('percent words')
fig.savefig(OUTPUT)
