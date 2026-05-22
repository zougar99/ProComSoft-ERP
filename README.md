# 🏪 ProComSoft ERP - Système de Gestion d'Entreprise

📦 Point of Sale (POS) et système ERP complet développé avec PyQt5 et SQLAlchemy.

## ✨ Fonctionnalités

### 🏪 Point de vente & ERP
- 🛒 **Point de vente (POS)** : Interface de caisse avec panier, recherche produits, remises
- 👥 **Gestion des clients** : CRM complet avec historique des ventes
- 📦 **Gestion des produits** : Inventaire avec suivi des stocks et alertes de réapprovisionnement
- 🧾 **Facturation** : Création et gestion des factures avec calcul de TVA
- 💳 **Paiements** : Enregistrement des paiements (espèces, carte, chèque, virement)
- 📥 **Achats** : Gestion des commandes fournisseurs avec réception de stock
- 🏷️ **Promotions** : Campagnes promotionnelles avec coupons
- ⭐ **Fidélité** : Programme de points de fidélité clients

### 📊 Tableau de bord & Rapports
- 📊 **Tableau de bord** : Statistiques en temps réel (ventes du jour, stocks faibles)
- 📈 **Rapports** : Analyse des ventes par période avec filtres
- 🔐 **Utilisateurs** : Gestion des comptes et rôles (admin, manager, user, cashier)
- 💾 **Sauvegarde/Restauration** : Backup et restauration de la base de données
- 🌍 **Multilingue** : Arabe, Français, Anglais (détection automatique)
- ⚙️ **Paramètres** : Configuration de l'application (langue, devise, TVA)

### 🤖 AI & Analytics (Intelligence Artificielle)
- 📈 **Prévision des ventes** : 4 méthodes (moyenne mobile, lissage exponentiel, régression linéaire, saisonnalité) + prédiction ensembliste
- 🛒 **Recommandations produits** : Analyse du panier d'achat (Market Basket Analysis) avec règles d'association (lift, confiance, support)
- 👤 **Segmentation client RFM** : Récence, Fréquence, Montant avec 6 segments (Champion, Loyal, Potentiel, À risque, Perdu, Nouveau)
- ⚠️ **Détection d'anomalies** : Transactions suspectes et pics/baisse de ventes (z-score)
- 💰 **Optimisation des prix** : Analyse des marges, suggestions de prix dynamiques
- 📦 **Gestion intelligente des stocks** : Calcul EOQ, point de réapprovisionnement, alertes de rupture
- 🔮 **Prédiction de churn** : Identification des clients à risque de départ
- 💵 **Prévision de trésorerie** : Projection des flux entrants/sortants
- 🏆 **Valeur client (CLV)** : Calcul et segmentation de la valeur client
- ❤️ **Score de santé** : Indicateur global de santé de l'entreprise (0-100)

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
├── ai_module.py         # 🤖 Module IA complet (prévisions, recommandations, détection)
├── ai_insights_tab.py   # 🤖 Interface des insights IA
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

## 🤖 AI Module - Classes disponibles

| Classe | Méthodes | Description |
|--------|----------|-------------|
| `AdvancedForecaster` | `moving_average()`, `exponential_smoothing()`, `linear_regression()`, `seasonal_forecast()`, `ensemble_forecast()` | Prévisions de ventes multi-méthodes |
| `MarketBasketAnalyzer` | `get_association_rules()`, `suggest_bundle()` | Analyse du panier d'achat (règles d'association) |
| `CustomerAnalytics` | `rfm_segmentation()`, `churn_prediction()`, `customer_lifetime_value()`, `purchase_behavior_analysis()` | Analytics clients avancés |
| `AnomalyDetector` | `detect_sales_anomalies()`, `detect_unusual_transactions()` | Détection d'anomalies statistiques |
| `PriceOptimizer` | `price_elasticity()`, `suggest_dynamic_pricing()` | Optimisation et suggestion de prix |
| `InventoryIntelligence` | `reorder_recommendations()`, `stock_health_summary()` | Gestion intelligente des stocks |
| `BusinessIntelligence` | `cash_flow_forecast()`, `business_health_score()`, `revenue_breakdown()` | Santé globale de l'entreprise |

## 🗄️ Base de données

SQLite avec SQLAlchemy ORM. Tables principales :
- 👤 `users`, 👥 `customers`, 🏭 `suppliers`, 📦 `products`, 📂 `categories`
- 🧾 `sales`, 📝 `sale_items`, 📄 `invoices`, 💳 `payments`
- 📥 `purchases`, 📋 `purchase_items`
- 🏠 `warehouses`, 📊 `inventory_items`
- 💰 `accounts`, 📒 `journal_entries`

## 📜 Licence

© ProComSoft ERP - Tous droits réservés
