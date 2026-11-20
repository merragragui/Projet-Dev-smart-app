import xml.etree.ElementTree as ET
from pathlib import Path
import cv2, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path("data/raw/NEU-DET")

# Index de toutes les images (par nom sans extension)
imgs = {}
for ext in (".jpg", ".jpeg", ".png", ".bmp"):
    for p in ROOT.rglob(f"*{ext}"):
        imgs[p.stem] = p
print("Images trouvées :", len(imgs))

rows = []
for xml_path in ROOT.rglob("*.xml"):
    root = ET.parse(xml_path).getroot()
    stem = xml_path.stem
    if stem not in imgs:
        continue
    W = int(root.find("size/width").text)
    H = int(root.find("size/height").text)
    for obj in root.findall("object"):
        bb = obj.find("bndbox")
        x1, y1, x2, y2 = (int(float(bb.find(k).text)) for k in ("xmin", "ymin", "xmax", "ymax"))
        rows.append(dict(image=stem, path=str(imgs[stem]), classe=obj.find("name").text,
                         W=W, H=H, x1=x1, y1=y1, x2=x2, y2=y2,
                         aire_rel=((x2 - x1) * (y2 - y1)) / (W * H)))

df = pd.DataFrame(rows)
df.to_csv("data/annotations.csv", index=False)
print("Images annotées :", df.image.nunique(), "| Boîtes :", len(df))
print(df.classe.value_counts())
print(df.groupby("classe").aire_rel.describe().round(3))
print("Images avec plusieurs boîtes :", (df.groupby("image").size() > 1).sum())

# Luminosité et contraste par classe
st = []
for _, r in df.drop_duplicates("image").iterrows():
    g = cv2.imread(r.path, cv2.IMREAD_GRAYSCALE)
    st.append(dict(classe=r.classe, mean=g.mean(), std=g.std()))
st = pd.DataFrame(st)
print(st.groupby("classe").mean().round(1))

fig, ax = plt.subplots(1, 3, figsize=(17, 4))
df.classe.value_counts().plot.bar(ax=ax[0], title="Boîtes par classe")
df.boxplot(column="aire_rel", by="classe", ax=ax[1]); ax[1].set_title("Taille relative")
st.boxplot(column="mean", by="classe", ax=ax[2]); ax[2].set_title("Luminosité moyenne")
plt.suptitle(""); plt.tight_layout(); plt.savefig("data/eda.png", dpi=120)

fig, ax = plt.subplots(2, 3, figsize=(12, 8))
for a, (c, g) in zip(ax.ravel(), df.groupby("classe")):
    r = g.iloc[0]
    img = cv2.imread(r.path)
    cv2.rectangle(img, (r.x1, r.y1), (r.x2, r.y2), (0, 0, 255), 2)
    a.imshow(img[..., ::-1]); a.set_title(c); a.axis("off")
plt.tight_layout(); plt.savefig("data/exemples.png", dpi=120)