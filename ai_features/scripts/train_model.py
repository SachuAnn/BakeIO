import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib
import os

def train_model():
    # Load dataset
    df = pd.read_csv('ai_features/data/cake_prices.csv')
    
    X = df.drop('price', axis=1)
    y = df['price']
    
    # Preprocessing
    categorical_features = ['flavor', 'complexity', 'occasion']
    numerical_features = ['tiers', 'weight']
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', 'passthrough', numerical_features),
            ('cat', OneHotEncoder(drop='first'), categorical_features)
        ])
    
    # Model pipeline
    model = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', RandomForestRegressor(n_estimators=100, random_state=42))
    ])
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train
    model.fit(X_train, y_train)
    
    # Save model
    os.makedirs('ai_features/models', exist_ok=True)
    joblib.dump(model, 'ai_features/models/price_model.pkl')
    
    print("Model trained and saved to ai_features/models/price_model.pkl")
    print(f"Training Score: {model.score(X_train, y_train):.4f}")
    print(f"Test Score: {model.score(X_test, y_test):.4f}")

if __name__ == "__main__":
    train_model()
