# TP1 DSP — Lecture et traitement des données vidéo

Cette solution répond à la partie développement du TP1 sur l'adressage
mémoire d'une image CIF en YUV 4:2:0 et sur le transfert SRC vers DST.

## Structure

- [`src/tp1_dsp.py`](src/tp1_dsp.py) : calcul d'adresses et copie des trois plans.
- [`tests/test_tp1_dsp.py`](tests/test_tp1_dsp.py) : tests des résultats demandés
  et des cas invalides.
- `TP1_DSP.pdf` : énoncé fourni.

Le code utilise uniquement la bibliothèque standard Python. L'environnement
`.venv` n'est pas inclus dans le dépôt.

## Données de l'énoncé

La résolution CIF est `352 x 288`.

| Plan | Dimensions | Taille |
|---|---:|---:|
| Y | `352 x 288` | `101376 = 0x18c00` octets |
| U | `176 x 144` | `25344 = 0x6300` octets |
| V | `176 x 144` | `25344 = 0x6300` octets |

Une image complète occupe donc `152064 = 0x25200` octets. Les adresses de
base données dans le sujet sont :

| Plan | Base source |
|---|---:|
| Y | `0x00ec470` |
| U | `0x00105070` |
| V | `0x0010b370` |

## Méthode de calcul

Pour un pixel de luminance `(x, y)` :

```text
adresse_Y = base_Y + frame * 0x25200 + y * 352 + x
```

Le sous-échantillonnage 4:2:0 associe un échantillon chroma à un bloc 2x2 de
luminance. On utilise donc `x_U = x // 2`, `y_U = y // 2` et `largeur_U = 176` :

```text
adresse_U/V = base_U/V + frame * 0x25200 + (y // 2) * 176 + (x // 2)
```

Les divisions sont entières : les coordonnées `(44, 120)` et `(45, 121)`
pointent par exemple vers le même échantillon chroma.

## Résultats demandés

### Frame 0, point `(45, 120)`

Offsets dans les plans :

- Y : `120 * 352 + 45 = 42285 = 0xa4cd`
- U/V : `(120 // 2) * 176 + (45 // 2) = 10582 = 0x2956`

Adresses calculées :

| Plan | Calcul | Adresse |
|---|---|---:|
| Y | `0x00ec470 + 0xa4cd` | **`0x0f699d`** |
| U | `0x00105070 + 0x2956` | **`0x1079c6`** |
| V | `0x0010b370 + 0x2956` | **`0x10dcc6`** |

### Frame 7, point `(200, 60)`

Le sujet charge les images une par une dans le code C. Pour modéliser les
frames dans un buffer contigu, la frame 7 ajoute `7 * 0x25200 = 0x102600`
à chaque base.

Offsets dans les plans :

- Y : `60 * 352 + 200 = 21320 = 0x5348`
- U/V : `(60 // 2) * 176 + (200 // 2) = 5380 = 0x1504`

Adresses calculées dans un buffer contigu :

| Plan | Calcul | Adresse |
|---|---|---:|
| Y | `0x00ec470 + 0x102600 + 0x5348` | **`0x1f55b8`** |
| U | `0x00105070 + 0x102600 + 0x1504` | **`0x20a374`** |
| V | `0x0010b370 + 0x102600 + 0x1504` | **`0x210674`** |

Si chaque frame est chargée dans le même buffer externe, comme dans le
programme C du sujet, il faut omettre le terme `frame * 0x25200` : les adresses
deviennent alors celles de la frame courante, avec les mêmes offsets
`0x5348` et `0x1504`.

## Transfert SRC vers DST

`copy_yuv420_frame` reproduit le comportement du code C : il copie séparément
les `101376` octets de Y, puis les `25344` octets de U et enfin les `25344`
octets de V. Les tailles des buffers et les dimensions sont contrôlées avant
la copie afin d'éviter un transfert incomplet.

## Exécution

Depuis la racine du projet :

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe .\src\tp1_dsp.py
```
