# 🏪 ProComSoft ERP - Système de Gestion d'Entreprise

📦 Point of Sale (POS) et système ERP complet développé avec PyQt5 et SQLAlchemy.

## ✨ Fonctionnalités

- 🛒 **Point de vente (POS)** : Interface de caisse avec panier, recherche produits, remises
- 👥 **Gestion des clients** : CRM complet avec historique des ventes
- 📦 **Gestion des produits** : Inventaire avec suivi des stocks et alertes de réapprovisionnement
- 🧾 **Facturation** : Création et gestion des factures avec calcul de TVA
- 💳 **Paiements** : Enregistrement des paiements (espèces, carte, chèque, virement)
- 📊 **Tableau de bord** : Statistiques en temps réel (ventes du jour, stocks faibles)
- 📈 **Rapports** : Analyse des ventes par période
- 🔐 **Utilisateurs** : Gestion des comptes et rôles (admin, manager, user, cashier)
- 💾 **Sauvegarde/Restauration** : Backup et restauration de la base de données
- 🌍 **Multilingue** : Arabe, Français, Anglais (détection automatique)

## 🚀 Installation

```bash
# Cloner le dépôt
git clone <url-du-repo>
cd POS-System-v1

# Installer les dépendances
pip install PyQt5 SQLAlchemy bcrypt

# Lancer l'application
python main.py
```

## 👤 Première utilisation

- **Utilisateur** : `admin`
- **Mot de passe** : `admin`

## 📁 Structure du projet

```
POS-System-v1/
├── main.py              # 🚀 Point d'entrée
├── ui/                  # 🎨 Interface utilisateur (login, main window)
├── modules/             # 🧩 Modules métier (sales, crm, inventory, purchases)
├── services/            # ⚙️ Couche service
├── database/            # 🗄️ Modèles et connexion base de données
├── utils/               # 🔧 Utilitaires (i18n, security, helpers)
├── core/                # 🏗️ Fonctions noyau (exceptions, validators)
├── config/              # ⚙️ Configuration de l'application
├── data/                # 💿 Base de données et sauvegardes
├── reports/             # 📄 Rapports exportés
└── locales/             # 🌐 Fichiers de traduction JSON
```

## 🗄️ Base de données

SQLite avec SQLAlchemy ORM. Tables principales :
- 👤 `users`, 👥 `customers`, 🏭 `suppliers`, 📦 `products`, 📂 `categories`
- 🧾 `sales`, 📝 `sale_items`, 📄 `invoices`, 💳 `payments`
- 📥 `purchases`, 📋 `purchase_items`
- 🏠 `warehouses`, 📊 `inventory_items`
- 💰 `accounts`, 📒 `journal_entries`

## 📜 Licence

© ProComSoft ERP - Tous droits réservés
