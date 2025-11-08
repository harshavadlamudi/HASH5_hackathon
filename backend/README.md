# HealthLake AI Backend API

FastAPI backend for HealthLake AI Assistant.

## Setup

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Environment Variables
Create `.env` file in project root with:
```
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_SESSION_TOKEN=your_token
AWS_REGION=us-west-2
```

### Run Development Server
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### Access API
- API: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Endpoints

### Health Check
- `GET /api/health` - Check API health

### Patients
- `GET /api/patients` - List all patients
- `GET /api/patients/{id}` - Get patient by ID
- `GET /api/patients/{id}/summary` - Get patient summary

## Project Structure
```
backend/
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── health.py
│   │       └── patients.py
│   ├── core/
│   │   └── config.py
│   ├── models/
│   │   └── patient.py
│   ├── services/
│   │   └── healthlake_service.py
│   └── main.py
├── requirements.txt
└── README.md
```
