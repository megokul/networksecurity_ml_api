from fastapi import FastAPI, File, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from uvicorn import run as app_run
import pandas as pd
from pathlib import Path

from src.networksecurity.logging import logger
from src.networksecurity.exception.exception import NetworkSecurityError
from src.networksecurity.pipeline.training_pipeline import TrainingPipeline
from src.networksecurity.utils.core import load_object
from src.networksecurity.inference.estimator import NetworkModel

# Initialize FastAPI app
app = FastAPI(title="NetworkSecurity ML API", version="1.0")

templates = Jinja2Templates(directory="./templates")

# Allow CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === ROUTES ===

@app.get("/", tags=["authentication"])
async def index():
    return RedirectResponse(url="/docs")


@app.get("/train", tags=["pipeline"])
async def train_route():
    try:
        pipeline = TrainingPipeline()
        pipeline.run_pipeline()
        return Response(content="Training completed successfully.", media_type="text/plain")
    except Exception as e:
        raise NetworkSecurityError(e, logger)


@app.post("/predict", tags=["inference"])
async def predict_route(request: Request, file: UploadFile = File(...)):
    try:
        df = pd.read_csv(file.file)

        # Load final model and preprocessors
        model = load_object(Path("final_model/final_inference_model.joblib"))
        if not isinstance(model, NetworkModel):
            raise TypeError("Loaded object is not a NetworkModel instance.")

        # Perform prediction
        y_pred = model.predict(df)
        df["predicted_column"] = y_pred

        # Save output and return as HTML table
        output_path = Path("prediction_output/output.csv")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)

        html_table = df.to_html(classes="table table-striped")
        return templates.TemplateResponse("table.html", {"request": request, "table": html_table})

    except Exception as e:
        raise NetworkSecurityError(e, logger)

if __name__ == "__main__":
    app_run(app, host="0.0.0.0", port=8000)