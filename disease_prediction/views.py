import os
import pickle
import numpy as np
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin

# Load the trained model
# Load the XGBoost trained model
model_path = os.path.join(os.path.dirname(__file__), "disease_model_xgb.pkl")
with open(model_path, "rb") as file:
    model_data = pickle.load(file)

# Extract model components
model = model_data['model']
scaler = model_data['scaler']
label_encoder = model_data['label_encoder']  # Added label encoder
symptoms_list = model_data['symptoms_list']
possible_diseases = model_data['diseases']  # Already label encoded in training


# Doctor recommendations mapping
DOCTOR_MAPPING = {
    "Fungal infection": ["Dermatologist"],
    "Allergy": ["Allergist", "Immunologist"],
    "GERD": ["Gastroenterologist"],
    "Chronic cholestasis": ["Hepatologist", "Gastroenterologist"],
    "Drug Reaction": ["Allergist", "Dermatologist"],
    "Peptic ulcer disease": ["Gastroenterologist"],
    "AIDS": ["Infectious Disease Specialist"],
    "Diabetes": ["Endocrinologist"],
    "Gastroenteritis": ["Gastroenterologist"],
    "Bronchial Asthma": ["Pulmonologist", "Allergist"],
}

# Diet and Exercise recommendations
DIET_MAPPING = {
    "Fungal infection": ["Probiotic-rich foods", "Anti-inflammatory foods", "Garlic", "Coconut oil"],
    "Allergy": ["Anti-inflammatory foods", "Local honey", "Vitamin C rich foods", "Quercetin-rich foods"],
    "Diabetes": ["Low-glycemic foods", "High-fiber foods", "Lean proteins", "Healthy fats"],
}

EXERCISE_MAPPING = {
    "Fungal infection": ["Regular moderate exercise", "Keeping affected areas dry"],
    "Allergy": ["Indoor exercises during high pollen", "Swimming", "Yoga"],
    "Diabetes": ["Regular cardio", "Strength training", "Yoga", "Walking"],
}

@method_decorator(ensure_csrf_cookie, name='dispatch')
class DiseasePredictionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Get symptoms from request
        reported_symptoms = request.data.get("symptoms", [])
        
        if not reported_symptoms:
            return Response({"error": "Please provide at least one symptom."}, status=400)

        # Create symptom vector (0s and 1s)
        symptom_vector = np.zeros(len(symptoms_list))
        for symptom in reported_symptoms:
            if symptom in symptoms_list:
                symptom_index = symptoms_list.index(symptom)
                symptom_vector[symptom_index] = 1
        
        # Apply the same scaling used during training
        symptom_vector = scaler.transform([symptom_vector])

        # Make prediction
        # Predict disease probabilities
        probabilities = model.predict_proba(symptom_vector)[0]

                # Convert numeric prediction indices back to disease names
        top_3_indices = np.argsort(probabilities)[-3:][::-1]  # Get top 3 predictions
        top_3_diseases = [(possible_diseases[i], round(probabilities[i] * 100, 2)) for i in top_3_indices]

        
        # Get recommendations for top predicted disease
        primary_disease, confidence_score = top_3_diseases[0]
        recommended_doctors = DOCTOR_MAPPING.get(primary_disease, ["General Physician"])
        recommended_diet = DIET_MAPPING.get(primary_disease, ["Maintain a balanced diet", "Stay hydrated"])
        recommended_exercise = EXERCISE_MAPPING.get(primary_disease, ["Regular moderate exercise", "Consult doctor before starting any exercise routine"])

        return Response({
            "predicted_disease": primary_disease,
            "confidence_score": f"{confidence_score}%",
            "top_3_predictions": top_3_diseases,
            "recommended_doctors": recommended_doctors,
            "recommended_diet": recommended_diet,
            "recommended_exercise": recommended_exercise
        })

    def get(self, request):
        """Return the list of all possible symptoms"""
        return Response({
            "symptoms": symptoms_list,
            "possible_diseases": possible_diseases
        })
    

class DiseasePredictionResultView(LoginRequiredMixin, TemplateView):
    template_name = 'disease_prediction/prediction_results.html'
    
    def post(self, request, *args, **kwargs):
        # Get symptoms from POST data
        reported_symptoms = request.POST.getlist("symptoms")
        
        if not reported_symptoms:
            # Redirect back to prediction page with error message
            from django.contrib import messages
            messages.error(request, "Please select at least one symptom.")
            return redirect('disease_prediction:predict')

        # Create symptom vector (0s and 1s)
        symptom_vector = np.zeros(len(symptoms_list))
        for symptom in reported_symptoms:
            if symptom in symptoms_list:
                symptom_index = symptoms_list.index(symptom)
                symptom_vector[symptom_index] = 1
        
        # Apply scaling
        symptom_vector = scaler.transform([symptom_vector])

        # Make prediction
        # Predict disease probabilities
        probabilities = model.predict_proba(symptom_vector)[0]

# Convert numeric prediction indices back to disease names
        top_3_indices = np.argsort(probabilities)[-3:][::-1]  # Get top 3 predictions
        top_3_diseases = [(possible_diseases[i], round(probabilities[i] * 100, 2)) for i in top_3_indices]

        
        # Get recommendations
        primary_disease, confidence_score = top_3_diseases[0]
        recommended_doctors = DOCTOR_MAPPING.get(primary_disease, ["General Physician"])
        recommended_diet = DIET_MAPPING.get(primary_disease, ["Maintain a balanced diet", "Stay hydrated"])
        recommended_exercise = EXERCISE_MAPPING.get(primary_disease, ["Regular moderate exercise", "Consult doctor before starting any exercise routine"])

        # Prepare context for template
        context = self.get_context_data(**kwargs)
        context.update({
            "predicted_disease": f"{primary_disease} ({confidence_score}% confidence)",
            "top_3_predictions": top_3_diseases,
            "recommended_doctors": recommended_doctors,
            "recommended_diet": recommended_diet,
            "recommended_exercise": recommended_exercise,
            "selected_symptoms": reported_symptoms
        })
        
        return self.render_to_response(context)
