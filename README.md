# mental-health-companion
An AI-powered mental health chatbot that provides empathetic support and resources for mental wellness. Built with Python, Ollama, and mental health datasets

## BUILD PROCESS
##
git clone https://github.com/ABAbdulah/mental-health-companion.git
cd mental-health-companion
## For Backend. 
python -m venv venv
# venv\Scripts\activate
### pip install -r requirements.txt
uvicorn backend.main:app --reload

## For Frontend
cd frontend
npm i
npm run dev
