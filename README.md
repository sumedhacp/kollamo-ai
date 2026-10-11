# Kollamo.ai

Malayalam-English Code-Mixed (Manglish) Social Media Sentiment Engine.

## Tech Stack
- **Backend:** Python 3.10+, FastAPI, PyTorch, Hugging Face Transformers (MuRIL)
- **Frontend:** React (Vite), Tailwind CSS, Recharts, Lucide React
- **Comment Ingestion:** YouTube Data API v3 & fallback scrapers

## Project Architecture
- **Zone 1:** Single-Text Sandbox (Ad-hoc manual inspection & instant inference)
- **Zone 2:** Social Media Link Ingestion (Batch/checkbox comment extractor)
- **Zone 3:** Interactive Sentiment Dashboard (Pie/Bar distribution & filtering)