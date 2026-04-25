# Findings - GraphCast Ingestion

## Research & Discoveries

### GraphCast Content Analysis
- **Domain**: AI Weather Forecasting (DeepMind).
- **Key Concepts**: ERA5 data, HRES comparison, Data Assimilation Windows (Lookahead), Multi-mesh (Icosahedron), MSE vs Blurring, Stratosphere weight (50 hPa), Tropical Cyclones (Survivor Bias).
- **Language**: Italian.
- **Complexity**: High. Requires precise chunking to not split questions from answers.

### System State
- **DB**: Singleton `/app/data/rag_storage.db` (Named Volume).
- **Model**: `all-MiniLM-L6-v2`.
- **Status**: Operational, fixed disk I/O issues.
