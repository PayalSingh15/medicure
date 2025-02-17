from django.urls import path
from .views import DiseasePredictionView, DiseasePredictionResultView
from django.views.generic import TemplateView

app_name = 'disease_prediction'  # This means we need to use the namespace

urlpatterns = [
    # Notice our URL names have changed
    path("predict/api/", DiseasePredictionView.as_view(), name="predict-disease-api"),
    path("", TemplateView.as_view(template_name="disease_prediction/predict.html"), name="predict"),  # Changed from predict-disease
    path("results/", DiseasePredictionResultView.as_view(), name="predict_results"),
]