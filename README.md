# RLC
Implémentons le protocole RLC en AM !!!

---

## Structure des fichiers

```
RLC/
│
├── sender.py       # Émetteur Python RLC-AM
├── receiver.py     # Récepteur Python RLC-AM
├── server.js       # Serveur Node.js de simulation
└── config.json     # Configuration des scénarios de perte/réord.
```
Il y a les `package.json` et `package-lock.json` (entre nous ... n'y touchons pas 🤐) 

Ah la `LICENSE` c'est pour garder le statut quo (juste une GPL-3.0 license)

Le `README.md` c'est un petit guide (ha ha 🤐)

## Comment faire la simulation ?

### Installer les dépendances Node.js

```cmd
npm install
```

### Personnaliser la qualité réseau

Pour cela modifier le fichier `config.json`

```json
{
  "lossRate": 0.1,
  "duplicationRate": 0.05,
  "reorderRate": 0.1,
  "maxDelayMs": 200
}
```
Allez, soyez pas timides, modifiez comme vous voulez les valeurs (mais ne changez pas la structure 🤐)

### Lancer le serveur

```cmd
node server.js
```

### Lancer le récepteur

```cmd
python3 receiver.py
```

### Lancer le récepteur

```cmd
python3 sender.py chemin/vers/ton/fichier
```

### Pour arrêter 

Lancer des KeyboardInterrupt sur chacun des terminaux (où vous avez lancé le receiver, le sender, et le server) avec `Crtl + C`

Dans une prochaine version les programmes s'arrêteront tous seuls (peut être 🤐)

---

Laissez une étoile si vous avez assez aimé (C'est mignon, non ? 🤐)

---
