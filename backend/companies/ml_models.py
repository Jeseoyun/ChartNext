from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR

def train_models(X, y):
    models = {
        'LinearRegression': LinearRegression(),
        'RandomForest': RandomForestRegressor(),
        'SVR': SVR(),
    }
    trained_models = {}
    for name, model in models.items():
        model.fit(X, y)
        trained_models[name] = model
    return trained_models 