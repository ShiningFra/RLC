# RLC
Implémentons le protocole RLC en AM !!!

## Structure des fichiers

```
rlc_am_test/
│
├── sender.py       # Émetteur Python RLC-AM
├── receiver.py     # Récepteur Python RLC-AM
├── server.js       # Serveur Node.js de simulation
└── config.json     # Configuration des scénarios de perte/réord.
```

## Comment faire la simulation ?

### Installer les dépendances Node.js

```cmd
npm install
```

### Personnaliser la qualité réseau

Pour cela modifier le fichier `config.json`

```json
{
  "lossRate": 0.1,         // Probabilité de perte d'un PDU (0.0 à 1.0)
  "duplicationRate": 0.05, // Probabilité de dupliquer un PDU
  "reorderRate": 0.1,      // Probabilité de différer un PDU
  "maxDelayMs": 200        // Délai max en ms pour réordonnancer
}
```

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
