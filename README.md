
# 🌍 Natural Catastrophe Event Detection and Clustering

## 📘 Project Purpose

This repository addresses the problem of detecting, processing, and clustering global news articles related to natural catastrophes. The goal is to build a pipeline that takes in raw news article metadata, extracts meaningful disaster-related insights, and clusters similar articles together based on both textual and structured signals.

The motivation stems from the need to automate real-time understanding and categorization of disaster-related news to support humanitarian efforts, early warning systems, and trend analysis. 

---

## 📂 Dataset Overview

The original dataset used in this project is located in the `data/` folder and includes the file:
- **`Nat Cat Events.csv`** 

It consists of **91,479 English-language articles** covering natural disasters across **135 countries** and sourced from over **5,800 unique domains**. Articles are annotated with publication time, URL, title, language, domain, and source country, with some fields like mobile URL and social image occasionally missing.

---

## 🔍 Phase 1: Exploratory Data Analysis (EDA)

I began by thoroughly exploring the dataset to understand its structure, quality, and potential challenges.

### Key Findings:
- **Geographic Skew**: A heavy concentration of articles from the United States (65%).
- **Temporal Patterns**: Articles peak around midnight, likely due to automated scheduling.
- **Duplicates**: Over 2,100 exact duplicate rows and 26,000+ duplicate titles, likely from syndication.
- **Missing Data**: `url_mobile` was missing in over 72% of rows, and `socialimage` in 13%.
- **Title Characteristics**: Most titles ranged between 40–90 characters and showed consistent formatting.
- **Disaster Themes**: Words like “earthquake,” “flood,” “storm,” and “volcano” were among the most frequent — confirming the thematic focus.

These findings helped shape my data cleaning and modeling strategy.

---

## 🧹 Phase 2: Data Cleaning (`part_1_data_cleaning.ipynb`)

After EDA, I developed a robust data cleaning process to prepare the dataset for downstream analysis.

### Key Cleaning Steps:
- **Removed duplicates** to ensure that each row represented a unique disaster event.
- **Normalized titles** by fixing encoding issues and removing non-ASCII characters.
- **Parsed domains** using `tldextract` to create subdomain, domain_root, and TLD features. 
  - I hypothesized that `subdomain` might hold semantic signals (e.g., "volcano", "alerts"), but due to high missingness, it wasn’t used further.
- **Checked URL quality**, flagging broken links based on patterns like “404” or unreachable domains.
- **Extracted locations** using `spaCy` NER to create `locations` and `has_location` flags.
- **Matched disaster keywords** to titles using a curated list (e.g., earthquake, flood, wildfire).

As a result, I isolated **20,599 high-quality rows** that had both a recognized location and disaster keyword match.

---

## 🧠 Phase 3: Comparing Extraction Strategies — spaCy vs Transformers

To better detect and structure disaster events, I experimented with two entity extraction strategies:
- **spaCy NER** (`nat_cat_part_2_spacy_data.ipynb`)
- **Transformer-Based NER** (`nat_cat_part_2_transformers_data.ipynb`)

### Why the Comparison?
I wanted to test if **deeper contextual models (Transformers)** could improve disaster detection accuracy over **lightweight, rule-based systems** like spaCy. This was especially relevant since real-world news titles can be ambiguous or noisy.

### Differences in Implementation:
- The **spaCy pipeline** used rule-based keyword matching with a broader list of disaster types (including landslide, mudslide, etc.).
- The **transformer pipeline** used a pretrained BERT-based model to extract NER locations with higher semantic precision and rule based event indicators.

The transformer model produced a **larger and cleaner dataset (23,634 rows)** compared to the spaCy version (20,599 rows), highlighting its superior recall and relevance.

---

## 📈 Phase 4: Clustering Disaster Events

After enriching the dataset, I applied clustering algorithms to group similar events.

### Feature Selection:
I selected features based on both structure and semantics:
- **`matched_keyword`** — to guide clustering around disaster types
- **`season` and `month`** — based on clear seasonal trends discovered in EDA
- **`country_extracted`** — initially included, but later removed due to high cardinality and noise
- **Textual embeddings** — generated using `SentenceTransformer` to capture semantic similarity

### Clustering Results:
- **KMeans** initially performed best with a **silhouette score of ~0.85**, but results were skewed due to overrepresentation of earthquake events.
- I **balanced the classes** by downsampling, and **removed noisy features**, which lowered the silhouette score (~0.40) but **improved interpretability**.

Final clusters were more balanced, semantically meaningful, and aligned better with real-world event categories.

---

## ⚙️ Utility Functions (`utils.py`)

All core helper functions for domain parsing, Unicode normalization, URL checking, and title extraction are stored in `utils.py`. This file ensures that the workflow is clean, modular, and reusable. I created this file early on to centralize preprocessing logic and maintain reproducibility.

---

## ✅ Final Notes

This repository presents a complete NLP pipeline — from data ingestion to clustering — designed specifically for disaster-related news data. It demonstrates the trade-offs between speed and accuracy (spaCy vs Transformers), the importance of thoughtful feature design, and the impact of preprocessing on model performance.

Future work could include:
- Expanding entity extraction beyond titles (e.g., full article bodies)
- Real-time ingestion and classification of news feeds


---

## 🗂 Repository Structure

This repository is organized into the following files and folders:

```
├── data/
│   ├── raw_global_disaster_dataset.csv         # Original dataset
│   ├── data_processed_transformers.csv         # Cleaned & enriched dataset via transformer pipeline
│   ├── data_spacy_rule_based.csv               # Cleaned & enriched dataset via rule-based pipeline
│
├── part_1_data_cleaning.ipynb                  # Data cleaning and feature engineering pipeline
├── nat_cat_part_2_transformers_data.ipynb      # NER + clustering using transformer models
├── nat_cat_part_2_spacy_data.ipynb             # NER + clustering using spaCy and rule-based matching
├── final_clustering_comparison.ipynb           # Final clustering improvements and evaluation
│
├── utils.py                                    # Modular helper functions (e.g., title cleaning, domain parsing)
├── README_human_written.md                     # Final report-style README
```

---

## 🐍 Environment

- **Python Version**: 3.12
- Key libraries: `pandas`, `numpy`, `scikit-learn`, `spacy`, `transformers`, `sentence-transformers`, `pycountry`, `tldextract`, `beautifulsoup4`

---



### Clustering Model Comparison

I tested three clustering algorithms to determine which worked best for grouping disaster-related articles:

- **KMeans**: Delivered the best results in terms of cohesion and separation (initial silhouette score ~0.85). Final version used after feature refinement and balancing.
- **Agglomerative Clustering**: Formed meaningful clusters in some cases but was more sensitive to noise and less scalable.
- **DBSCAN**: Struggled with sparse clusters and parameter sensitivity, especially in the presence of unbalanced classes.

### spaCy vs Transformer NER Comparison

The transformer-based NER method consistently outperformed the spaCy approach in terms of relevance, contextual awareness, and clustering effectiveness. The transformer pipeline extracted a larger number of accurate, disaster-related events and resulted in significantly higher silhouette scores and more interpretable clusters.

---

### 📘 Notebook Documentation

All major **methodology steps, decisions, and key findings** are also described within the Jupyter notebooks as markdown cells. These explanations mirror the logical flow outlined in this README and help make the notebooks fully self-contained and easy to follow.
