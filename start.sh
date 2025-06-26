#!/usr/bin/env bash
# Launch FastAPI in the background
uvicorn api.main:app --host 0.0.0.0 --port 8000 &
# Launch Streamlit
streamlit run app/streamlit_app.py --server.port $PORT
