# Marketing LLM Tool

AI-native marketing platform — text via Claude, images via Flux, video via Veo.

## Run locally

### Backend
cd backend
python -m venv .venv
..venv\Scripts\python.exe -m pip install -r requirements.txt
..venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload



### Frontend
cd frontend
npm install
npm run dev



Then open http://localhost:5173.