all:

venv:
	@echo "🐍 Creating virtual environment"
	python3 -m venv ~/venv

req:
	@echo "📦 Installing requirements"
	pip install -r requirements.txt

stream: venv req
	@echo "✨ Starting streamlit"
	streamlit run app/app.py

api: ven req
	@echo "🚀 Starting API"
	uvicorn fastapi_app:app --reload  # --reload to reload server on changes
