from celery import Celery
from src.networksecurity.pipeline.training_pipeline import TrainingPipeline

celery_app = Celery(
    "networksecurity_tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
)

@celery_app.task(name="trigger_training_task")
def trigger_training_task():
    pipeline = TrainingPipeline()
    pipeline.run_pipeline()
