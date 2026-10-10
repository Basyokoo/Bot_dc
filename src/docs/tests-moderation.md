# Cas de test — brique « Modération → MariaDB »

Dernière mise à jour : 10/10/2026
Statut : brouillon, à compléter avant la clôture de la brique (Definition of Done).

## Conventions

- Chaque cas suit la forme « je fais ... → je m'attends à ... ».
- « Aucune ligne » signifie : aucune insertion dans la table des sanctions.
- Statuts : `P` = en cours, `F` = terminée, `I` = terminée mais retrait impossible pour une raison métier définitive.
- Les rangs sont comparés par leur pouvoir. Le sens de la numérotation des niveaux (plus grand = plus puissant, ou l'inverse) est fixé dans le MLD : les cas ci-dessous n'en dépendent pas.

## 1. Commande `warn`

| Id | Cas | Je fais | Résultat attendu |
|----|-----|---------|------------------|
| W1 | Normal | `warn @Jean spam`, l'auteur a la permission requise et un rang de pouvoir strictement supérieur à celui de Jean | Le bot confirme et indique le numéro du warn (calculé). Une ligne est créée : type `W`, statut `P`, serveur = serveur courant, cible = Jean, auteur = l'auteur, date_debut = maintenant (UTC), date_fin = `NULL`, motif = `spam`, rang_avant = `NULL` |
| W2 | Limite : rang égal | L'auteur et Jean ont le même pouvoir | Le bot refuse. Aucune ligne |
| W3 | Hiérarchie : cible plus puissante | Le pouvoir de Jean est supérieur à celui de l'auteur | Le bot refuse. Aucune ligne |
| W4 | Hiérarchie : cible moins puissante | Le pouvoir de Jean est inférieur à celui de l'auteur | Le bot accepte. Même ligne qu'en W1 |
| W5 | Limite : emoji | `warn @Jean "spam 🚨"` | Le bot accepte. L'emoji est relu à l'identique en base (utf8mb4) |
| W6 | Limite : 255 caractères | Motif de 255 caractères après suppression des espaces en début et fin | Le bot accepte. Une ligne est créée |
| W7 | Erreur : 256 caractères | Motif de 256 caractères après suppression des espaces | Le bot refuse et indique la limite de 255. Aucune ligne |
| W8 | Limite : espaces seuls | `warn @Jean " "` | Le bot refuse. Aucune ligne |
| W9 | Limite : motif absent | `warn @Jean` | Le bot indique que le motif est obligatoire. Aucune ligne |
| W10 | Erreur : permission manquante | `warn @Jean spam` sans la permission requise | Le bot refuse. Aucune ligne |

## 2. Scheduler

| Id | Cas | Je fais | Résultat attendu |
|----|-----|---------|------------------|
| S1 | Normal : ban échu | Une sanction `B`, statut `P`, date de fin dépassée | Le scheduler vérifie l'état sur Discord, débannit si nécessaire, passe la sanction à `F` |
| S2 | Erreur temporaire : Discord indisponible (5xx, timeout) | Le scheduler traite une sanction échue | La sanction reste `P`, nouvel essai au tour suivant |
| S3 | Limite : limitation de débit (429) | Discord renvoie 429 | La sanction reste `P`, nouvel essai plus tard (vérifier ce que discord.py gère déjà seul) |
| S4 | Définitif : mute, membre parti | Une sanction `M`, statut `P`, date de fin dépassée, le membre a quitté le serveur | La sanction passe à `I`, sans tentatives répétées |
| S5 | Normal : ban déjà levé | Une sanction `B`, statut `P`, date de fin dépassée, Discord indique que le ban est introuvable | Le scheduler considère le débannissement comme fait et passe la sanction à `F` |
| S6 | Charge : sanctions non échues | Des sanctions `P` dont la date de fin est dans le futur | Elles sont ignorées, aucun appel à Discord pour elles |
| S7 | Charge : sélection | Plusieurs sanctions échues et plusieurs non échues | Seules les sanctions à traiter sont sélectionnées et vérifiées sur Discord |
| S8 | Même tour : échéance et pardon (proposé, à valider) | Une sanction échue qui a aussi un pardon | Un seul traitement effectif, statut final `F`, aucune erreur bloquante |
| S9 | Ban définitif pardonné (proposé, à valider) | Un ban sans date de fin, relié à un pardon | Le scheduler le repère, débannit, passe à `F` |

### Classification des erreurs Discord

| Erreur | Catégorie | Comportement attendu |
|--------|-----------|----------------------|
| 429 limite de requêtes | Temporaire | Garder `P`, respecter le délai indiqué par Discord |
| 500, 502, 503, 504 | Temporaire | Garder `P`, réessayer |
| Timeout ou erreur réseau | Temporaire | Garder `P`, réessayer |
| 401 authentification invalide | Configuration | Garder `P`, alerter l'administrateur, suspendre les essais rapides |
| 403 permissions insuffisantes | Configuration ou définitive selon le contexte | Garder `P` tant que le problème peut être corrigé |
| 404 introuvable | Selon l'opération | Ban déjà absent : terminé (`F`). Mute dont le membre est parti : `I` |

Le statut `I` représente une impossibilité métier définitive, jamais une simple panne technique. Les erreurs rencontrées et les transitions de statut sont journalisées.

## 3. Contraintes de la base

| Id | Cas | Je fais | Résultat attendu |
|----|-----|---------|------------------|
| B1 | Mute sans fin | Insérer type `M` avec date_fin `NULL` | La base refuse (CHECK) |
| B2 | Type absent | Insérer un type `NULL` | La base refuse (NOT NULL) |
| B3 | Type invalide | Insérer le type `X` | La base refuse (ENUM, mode strict) |
| B4 | Motif absent | Insérer un motif `NULL` | La base refuse (NOT NULL) |
| B5 | Motif trop long | Insérer un motif de plus de 255 caractères | La base refuse (mode strict) |
| B6 | Ban définitif | Insérer type `B` avec date_fin `NULL` | La base accepte |
| B7 | Warn sans fin | Insérer type `W` avec date_fin `NULL` | La base accepte |

## 4. Hors brique 1 (à reprendre si la fonctionnalité est retenue)

| Id | Cas | Je fais | Résultat attendu |
|----|-----|---------|------------------|
| H1 | Réadhésion avec mute en cours | Un membre ayant un mute `P` quitte le serveur puis revient avant la date de fin | Si la fonctionnalité est activée, le mute est retrouvé et réappliqué, sans nouvelle sanction en base (comportement de Discord à vérifier par un test) |
