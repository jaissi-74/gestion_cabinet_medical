# Carnet d'adresses — Mini-Projet Python

## Structure des fichiers

| Fichier | Rôle |
|---------|------|
| `contact.py` | Classe `Contact` (Partie 1) |
| `address_book.py` | Classes `AddressBook`, `AddressBookFile`, `AddressBookDB` (Parties 1, 2, 5) |
| `auth.py` | Module d'authentification SHA-256 (Partie 4) |
| `main.py` | Application console avec menu (Parties 1 & 2) |
| `gui.py` | Interface graphique Tkinter + login (Parties 3, 4, 8) |

---

## Comment lancer l'application

### Version console (Parties 1 & 2)
```bash
python main.py
```

### Version graphique (Parties 3, 4, 5, 8)
```bash
python gui.py
```
Identifiants par défaut : **admin / admin123**

---

## Partie 2 — Différence entre liste Python et fichier texte

| Critère | Liste Python | Fichier texte |
|---------|-------------|---------------|
| **Persistance** | Les données sont perdues à la fermeture du programme | Les données sont sauvegardées entre les sessions |
| **Vitesse** | Très rapide (tout en mémoire RAM) | Plus lent (lecture/écriture disque à chaque opération) |
| **Capacité** | Limitée par la RAM disponible | Limitée par l'espace disque (beaucoup plus grand) |
| **Simplicité** | Très simple à manipuler | Nécessite de gérer l'ouverture/fermeture du fichier |
| **Partage** | Impossible entre plusieurs utilisateurs | Le fichier peut être partagé ou copié |
| **Cas d'usage** | Données temporaires, calculs intermédiaires | Applications nécessitant de la persistance |

**Conclusion :** Pour un carnet d'adresses réel, le fichier est indispensable. La liste suffit pour des tests ou des données temporaires.

---

## Partie 5 — Pourquoi SQLite est meilleur que le fichier texte

- **Requêtes** : recherche, tri, filtrage sans relire tout le fichier
- **Intégrité** : contraintes UNIQUE, types de données garantis
- **Sécurité** : les comptes admins sont stockés dans la même base
- **Exportation** : synchronisation CSV depuis la base en un clic

---

## Fonctionnalités implémentées

- ✅ Partie 1 — Classes Contact et AddressBook (liste)
- ✅ Partie 2 — Stockage fichier texte, gestion doublons, validation email/téléphone
- ✅ Partie 3 — Interface Tkinter (frameH, frameM, frameB), Listbox triée, boutons
- ✅ Partie 4 — Authentification SHA-256, fenêtre de connexion Tkinter
- ✅ Partie 5 — Base SQLite, table contacts + table admins, export CSV
- ✅ Partie 8 — Champs supplémentaires : catégorie, adresse, entreprise
