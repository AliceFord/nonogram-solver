# c:\Users\olive\OneDrive\Pictures\Screenshots\Screenshot 2024-07-11 210357.png

from PIL import Image
import numpy as np

im = Image.open(r'C:\Users\olive\OneDrive\Pictures\Screenshots\Screenshot 2024-07-10 210618.png')
# im = Image.open(r"C:\Users\olive\OneDrive\Pictures\Screenshots\Screenshot 2024-07-10 202748.png")
sqrWidth = np.ceil(np.sqrt(im.size[0]*im.size[1])).astype(int)
im = im.resize((sqrWidth, sqrWidth))

# newWidth = 100

# im = im.resize((newWidth, newWidth),)

im = im.convert('1')
im.save('output.png')