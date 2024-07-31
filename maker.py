# c:\Users\olive\OneDrive\Pictures\Screenshots\Screenshot 2024-07-11 210357.png

from PIL import Image
import numpy as np

NEGATIVE = True

# im = Image.open(r"C:\Users\olive\OneDrive\Pictures\Screenshots\Screenshot 2024-07-31 235248.png")
im = Image.open(r"C:\Users\olive\OneDrive\Pictures\Screenshots\Screenshot 2024-07-31 225906.png")
sqrWidth = np.ceil(np.sqrt(im.size[0]*im.size[1])).astype(int)
im = im.resize((sqrWidth, sqrWidth))

N = 100

im = im.resize((N, N))

im = im.convert('1')

pix = im.load()

rows = []
cols = []

for i in range(N):
    cols.append([])
    current = 0
    for j in range(N):
        if pix[i, j] == (255 if not NEGATIVE else 0):
            if current != 0:
                cols[-1].append(current)
                current = 0
        else:
            current += 1

    if current != 0:
        cols[-1].append(current)
    cols[-1].append(0)

for i in range(N):
    rows.append([])
    current = 0
    for j in range(N):
        if pix[j, i] == (255 if not NEGATIVE else 0):
            if current != 0:
                rows[-1].append(current)
                current = 0
        else:
            current += 1
    
    if current != 0:
        rows[-1].append(current)
    rows[-1].append(0)

print("rows =", rows)
print("cols =", cols)

im.save('output.png')