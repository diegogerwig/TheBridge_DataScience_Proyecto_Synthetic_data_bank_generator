run: venv req stream

venv:
	@echo "🐍 Creating virtual environment"
	python3 -m venv ~/venv

req:
	@echo "📦 Installing requirements"
	pip install -r requirements.txt

stream:
	@echo "✨ Starting streamlit"
	streamlit run app/app.py


	
