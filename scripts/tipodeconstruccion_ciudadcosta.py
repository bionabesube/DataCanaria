import rasterio
from rasterio.plot import show
from matplotlib import pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap, BoundaryNorm
import matplotlib.patches as mpatches

img = rasterio.open('data/raw/GHS_BUILT_C_MSZ_E2018_GLOBE_R2023A_54009_10_V1_0_R14_C14.tif')
full_img = img.read()

clipped_img_area_metropolitana = full_img[:, 19500:21600, 4900:8550]
clipped_img_cdad_costa = full_img[:, 19500:21000, 7300:8550]
clipped_img_mvd = full_img[:, 19760:21600, 4900:7300]

def load_clr(path):
	mapping = {}
	with open(path, encoding='utf-8') as f:
		for line in f:
			line = line.strip()
			if not line or line.startswith('#'):
				continue
			parts = line.split()
			code = int(parts[0])
			r, g, b = map(int, parts[1:4])
			a = int(parts[4]) if len(parts) >= 5 else 255
			label = ' '.join(parts[5:]) if len(parts) > 5 else str(code)
			mapping[code] = ((r/255, g/255, b/255, a/255), label)
	return mapping

clr_path = 'data/raw/GHS_BUILT_C_MSZ_E2018_GLOBE_R2023A_54009_10_V1_0_R14_C14.clr'
clr = load_clr(clr_path)

codes = sorted(clr.keys())
colors = [clr[c][0] for c in codes]
labels = [clr[c][1] for c in codes]

cmap = ListedColormap(colors)
boundaries = [c - 0.5 for c in codes] + [codes[-1] + 0.5]
norm = BoundaryNorm(boundaries, ncolors=cmap.N, clip=True)

arr = clipped_img_mvd[0]
plt.figure(figsize=(8, 8))
plt.imshow(arr, cmap=cmap, norm=norm)
plt.axis('off')

# leyenda
patches = [mpatches.Patch(color=colors[i], label=f"{codes[i]}: {labels[i]}") for i in range(len(codes))]
plt.legend(handles=patches, bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
plt.show()

# Histograma por clases coloreado según el .clr (solo clases presentes en el recorte)
unique_vals, counts = np.unique(arr, return_counts=True)
present_vals = []
present_counts = []
present_colors = []
present_labels = []
for v, c in zip(unique_vals, counts):
	vi = int(v)
	if vi in clr:
		present_vals.append(vi)
		present_counts.append(int(c))
		present_colors.append(clr[vi][0])
		present_labels.append(f"{vi}: {clr[vi][1]}")

if not present_vals:
	print('No se encontraron clases del .clr en el recorte para generar el histograma')
else:
	plt.figure(figsize=(10, 4))
	x = np.arange(len(present_vals))
	plt.bar(x, present_counts, color=present_colors)
	plt.xticks(x, present_labels, rotation=45, ha='right')
	plt.ylabel('Frecuencia')
	plt.title('Histograma por clase (coloreado según .clr)')
	plt.tight_layout()
	plt.show()