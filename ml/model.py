import joblib
from app.config import settings

model_path = settings.model_path

def load_model():
    return joblib.load(model_path)
