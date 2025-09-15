# Spatial Bias Detection & Mitigation Platform

A platform for auditing and mitigating spatial bias in decision outputs.

It supports detecting geographic disparities in predicted or observed outcomes of interest, visualizing fairness metrics on maps, and applying mitigation strategies such as relabeling and threshold adjustment.

## Key Features

| Area | What it does | User outputs |
| :-- | :-- | :-- |
| Spatial Bias Detection | Audits for spatial bias using statistical tests and quantifies it using the Spatial Bias Index (SBI). | Interactive maps (population distribution, bias heatmaps), bias per region table |
| Spatial Bias Mitigation | Post-processes model outputs to reduce spatial bias using either relabeling or regional decision boundary adjustment, optimizing SBI with minimal model change. | Interactive maps (population, pre/post bias heatmaps, performed flips), pre/post performance metrics and bias tables, adjusted thresholds (for regional decision boundary adjustment) |

<!-- | Spatial Bias Detection - Mitigation | <ul><li>Audit: Audits for spatial bias though statistical testing and meassures it using the Spatial Bias Index (SBI)</li><li>Mitigation - Relabeling: Mitigates spatial bias by flipping predictions optimizing for the SBI score</li><li>Mitigation - Decision Boundaries Adjustment: Mitigates spatial bias by incorporating adjusted regional decision bounaries instead of the default global decision bounary, which is used to assign the prediction probabilities to positive/negative class, in a way to optimize for the SBI score and generalize to new instances</li></ul> | <ul><li>Audit: Displayes in interactive map the population distribution, the bias per region with color map highlighting regions with significant bias and table with the bias per region</li><li>Mitigation - Relabeling:  Displayes in interactive map the population distribution, the performed flips, the bias per region with color map highlighting regions with significant bias before and after mitigation, table with the bias per region before and after mitigation, performance metrics before and after mitigation</li><li>Mitigation - Decision Boundaries Adjustment: </li></ul>Same with Mitigation - Relabeling plus the adjusted decision bounaries in plot and as a downloable table|
| Spatial Bias Detection & Mitigation | Audits for spatial bias using statistical tests and mitigates it via relabeling or region-adjusted decision boundaries. | Interactive maps (bias heatmaps, flips, population), bias tables, performance metrics, downloadable plots |
| Spatial Bias Detection | Audits for spatial bias using statistical tests and quantifies it using the Spatial Bias Index (SBI). | Interactive maps(polulation distribution, bias heatmaps), bias per region table|
| Spatial Bias Mitigation | Mitigates detected spatial bias through post-processing using relabeling or regional decision boundary adjustment to optimize fairness (SBI) without minimal model change. | Interactive maps (polulation distribution, Pre/post-mitigation bias heatmaps, performed flips), Pre/post-mitigation performance metrics & bias tables, adjusted thresholds (only for regional decision boundary adjustment mode) | -->


## Architecture \& Tech Stack

| Layer | Technology |
| :-- | :-- |
| Backend API | Python 3.10 · FastAPI (REST) · Uvicorn (ASGI) |
| Front-end | Vue 3 · TypeScript · Vite · Tailwind CSS |
| Packaging | Conda environment (`environment.yml`) |

## Quick Start
### Run Locally
#### 1 · Clone and install

```bash
# Clone Repo

# Navigate to backend
cd backend

# Create and activate the Conda environment
conda env create -f environment.yml
conda activate spatial-bias-env

```

#### 2 Backend

```bash
# Ensure you are in backend
cd backend

# Ensure the environment is activated
conda activate DVE-common-env

# Run the backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

```


#### 3 Frontend

Create a .env file in the root of the project.
```env
# Enable or disable Keycloak auth
VITE_USE_KEYCLOAK=false

# Keycloak config
VITE_KEYCLOAK_URL=https://auth.yourdomain.com/auth
VITE_KEYCLOAK_REALM=your-realm
VITE_KEYCLOAK_CLIENT_ID=your-client-id

# Backend API URL
# For local development:
VITE_API_BASE_URL=http://localhost:8000

# Base URL (landing page)
VITE_BASE_URL=
```

Open a new terminal.

```bash
# From the root, navigate to frontend
cd frontend

# Install UI dependencies (first run only)
pnpm install

# Run the frontend
pnpm dev

```

### Run with Docker

The first run will need to build the container:
```bash
docker compose up --build
```

To run, without rebuild:
```bash
docker compose up
```



## Managing the Conda Environment

### Add packages

```bash
# edit environment.yml
conda env update --file environment.yml --prune
```

`--prune` removes packages no longer required.

### To recreate the Conda environment

```bash
conda env export --no-builds > environment.yml
```

## Using the User Interface

### Spatial Bias Detection & Mitigation
Modes:
`Audit` / `Mitigation (Relabeling)` / `Mitigation (Decision Bounaries Adjustement)`.


#### Spatial Bias Detection
1. **Upload Data (.json)**. If no input is provided, a toy example is preloaded.
<!-- ```bash
{
  "indiv_info": [                   // list with a record per instance
    {
      "y_pred": int,                // Binary Prediction
      "lat": float | null,          // Latitude
      "lon": float | null,          // Longtitude
      "y_true": int | null,         // Ground Truth
      "region_ids": [int] | null    // Region membership
    }
  ],
  "region_info": [                  // List with a record per region
    {
      "polygon": [[float, float]]   // Region polygon (list of [lat, lon] pairs)
    }
  ] | null
}
``` -->
2. **Configure Audit Settings**
- Fairness Notion: Equal Opportunity (True Positive Rates) or Statistical Parity (Positive Rates)
- Alternate Worlds: Number of Monte Carlo samples
- Significance Level: Confidence threshold for statistical tests

3. **Click `Perform Audit`**

4. **Results**
- Population Distribution: Interactive Map displaying individual locations by class and region boundaries.
- Identified Bias per Region: Interactive Map highlighting biased regions and expressing bias with heatmap (red = favored, blue = disfavored, gray = fair).
- Summary Statistics: Significance threshold, count of biased regions.
- Per Region Statistics: Table including SBI and significance per region (downloadable).


#### Spatial Bias Mitigation (Relabeling)
1. **Upload Data (.json)**. Same format as Audit mode

2. **Configure Audit Settings**

- Audit settings (as above), plus:
  - Budget Constraint: The maximum number of flips allowed.
  - Positive Rate Change Tolerance: Max deviation from original positive rate.
  - Approximate Solution: Whether to use approximation.
  - Work Limit:  Limits the work unit (approximately one second of computation per unit on a single thread)

3. **Click `Perform Mitigation`**

4. **Results**
- Metrics Comparison: Accuracy/Precision/Recall/F1/SBI before vs. after mitigation.
- Population Distribution: As in Audit.
- Prediction Changes (Flips): Interactive Map displaying points with label changes, colored by flip direction.
- Identified Bias per Region pre/post mitigation: Interactive Map highlighting biased regions and expressing bias with heatmap (red = favored, blue = disfavored, gray = fair).
- Summary Statistics pre/post mitigation: Significance threshold, count of biased regions.
- Per Region Statistics pre/post mitigation: Tables including SBI and significance per region (downloadable).
- Mitigated Predictions: Final prediction outputs (downloadable)

#### Spatial Bias Mitigation (Decision Bounaries Adjustement)

1. **Upload Data (.json)**. If no input is provided, a toy example is preloaded.
<!-- ```bash
{
  "fit_indiv_info": [               // list with a record per instance
    {
      "y_pred": int,                // Binary Prediction
      "y_pred_prob": float,         // Classification Probability  
      "lat": float | null,          // Latitude
      "lon": float | null,          // Longtitude
      "y_true": int | null,         // Ground Truth
      "region_ids": [int] | null    // Region Ids, where instance belongs to
    }
  ],
  "predict_indiv_info": [           // list with a record per instance
    {
      "y_pred": int,                // Binary Prediction
      "y_pred_prob": float,         // Classification Probability
      "lat": float | null,          // Latitude
      "lon": float | null,          // Longtitude
      "y_true": int | null,         // Ground Truth
      "region_ids": [int] | null    // Region Ids, where instance belongs to
    }
  ],
  "predict_region_info": [          // List with a record per region
    {
      "polygon": [[float, float]]   // Polygon expressed as a list of consecutive coordinates (list with 2 members)
    }
  ] | null
}
``` -->

2. **Configure Settings**
- Mitigation (relabeling) settings, plus:
  - Base Model Threshold: Original threshold used by the model (e.g., 0.5).

3. **Click `Perform Mitigation`**

4. **Results**
Everything from the Relabeling mode, plus:
- Per-Region Threshold Bar Plot pre/post mitigation: Visualizes thresholds per region with bias-based coloring
- Adjusted Thresholds per Region: Table with the new thresholds, and a tie-breaking probability per region, which if != -1, is used to classify an instance in case its probability equals the threshold.



## REST API Reference

| Method \& Path | Description |
| :-- | :-- |
| `POST /api/spatial-bias/audit` | Trigger bias audit. |
| `POST /api/spatial-bias/mitigate/relabel` | Relabelling mitigation endpoint. |
| `POST /api/spatial-bias/mitigate/threshold` | Threshold-based mitigation endpoint. |

## License

Apache 2.0.
