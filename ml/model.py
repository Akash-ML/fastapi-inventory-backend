import joblib

def load_model():
    return joblib.load("ml/model.pkl")

model = load_model()