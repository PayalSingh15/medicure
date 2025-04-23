import os
import pickle
import numpy as np
from django.shortcuts import render
from django.views import View
from django.conf import settings
from django.contrib import messages


# Load the trained model
model_path = os.path.join(settings.BASE_DIR, "health_prediction", "models", "mental_health_model.pkl")
with open(model_path, "rb") as file:
    model_data = pickle.load(file)


model = model_data["model"]
label_encoder = model_data["label_encoder"]

class HealthPredictionView(View):
    def get(self, request):
        return render(request, "health_prediction/index.html")  # New template


class MentalHealthView(View):
    def __init__(self):
        super().__init__()
        self.model = None
        self.label_encoder = None
        self._load_model()

    def _load_model(self):
        try:
            model_path = os.path.join(settings.BASE_DIR, "health_prediction", "models", "mental_health_model.pkl")
            with open(model_path, "rb") as file:
                model_data = pickle.load(file)
            self.model = model_data["model"]
            self.label_encoder = model_data["label_encoder"]
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            self.model = None
            self.label_encoder = None

    def get(self, request):
        return render(request, "health_prediction/mental_health.html")

    def post(self, request):
        if not self.model or not self.label_encoder:
            messages.error(request, "Sorry, the prediction service is currently unavailable.")
            return render(request, "health_prediction/mental_health.html")

        try:
            # Get and validate user input
            features = []
            feature_names = [
                "sadness", "euphoric", "exhausted", "sleep_dissorder", 
                "mood_swing", "suicidal_thoughts", "anorxia", "authority_respect",
                "try_explanation", "aggressive_response", "ignore_move_on",
                "nervous_break_down", "admit_mistakes", "overthinking",
                "sexual_activity", "concentration", "optimisim"
            ]
            
            for feature in feature_names:
                value = request.POST.get(feature)
                if value is None:
                    messages.error(request, f"Missing required field: {feature}")
                    return render(request, "health_prediction/mental_health.html")
                features.append(int(value))

            # Make prediction
            input_features = np.array([features])
            prediction = self.model.predict(input_features)[0]
            predicted_condition = self.label_encoder.inverse_transform([prediction])[0]

            return render(request, "health_prediction/mental_health_result.html", {
                "condition": predicted_condition
            })

        except ValueError as e:
            messages.error(request, "Invalid input values provided.")
            return render(request, "health_prediction/mental_health.html")
        except Exception as e:
            messages.error(request, "An error occurred while processing your request.")
            return render(request, "health_prediction/mental_health.html")
    

# Load the trained PCOS model
pcos_model_path = os.path.join(settings.BASE_DIR, "health_prediction", "models", "pcos_model.pkl")
with open(pcos_model_path, "rb") as file:
    pcos_model = pickle.load(file)

class PCOSView(View):
    def __init__(self):
        super().__init__()
        self.model = None
        self._load_model()

    def _load_model(self):
        try:
            model_path = os.path.join(settings.BASE_DIR, "health_prediction", "models", "pcos_model.pkl")
            with open(model_path, "rb") as file:
                model_data = pickle.load(file)
            self.model = model_data["model"]
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            self.model = None

    def get(self, request):
        # Add this method back to handle GET requests
        return render(request, "health_prediction/pcos.html")

    def post(self, request):
        if not self.model:
            messages.error(request, "Sorry, the prediction service is currently unavailable.")
            return render(request, "health_prediction/pcos.html")

        try:
            # Create a mapping between form field names and model feature names
            form_data = {
                'Age': float(request.POST.get('Age (in Years)')),
                'Weight': float(request.POST.get('Weight (in Kg)')),
                'Height': float(request.POST.get('Height (in Cm)')),
                'PeriodRegularity': float(request.POST.get('After how many months do you get your periods?')),
                'WeightGain': float(request.POST.get('Have you gained weight recently?')),
                'HairGrowth': float(request.POST.get('Do you have excessive body/facial hair growth?')),
                'SkinDarkening': float(request.POST.get('Are you noticing skin darkening recently?')),
                'HairLoss': float(request.POST.get('Do have hair loss/hair thinning/baldness?')),
                'Acne': float(request.POST.get('Do you have pimples/acne?')),
                'FastFood': float(request.POST.get('Do you eat fast food regularly?')),
                'Exercise': float(request.POST.get('Do you exercise regularly?')),
                'MoodSwings': float(request.POST.get('Do you experience mood swings?')),
                'RegularPeriods': float(request.POST.get('Are your periods regular?')),
                'PeriodDuration': float(request.POST.get('How long does your period last? (in Days)')),
                'BloodGroup': float(request.POST.get('Can you tell us your blood group?'))
            }

            # Convert to list in the correct order for the model
            features = [
                form_data['Age'], form_data['Weight'], form_data['Height'],
                form_data['PeriodRegularity'], form_data['WeightGain'],
                form_data['HairGrowth'], form_data['SkinDarkening'],
                form_data['HairLoss'], form_data['Acne'], form_data['FastFood'],
                form_data['Exercise'], form_data['MoodSwings'],
                form_data['RegularPeriods'], form_data['PeriodDuration'],
                form_data['BloodGroup']
            ]

            # Make prediction
            prediction = self.model.predict([features])[0]
            predicted_condition = "PCOS Detected" if prediction == 1 else "No PCOS Detected"

            return render(request, "health_prediction/pcos_result.html", {
                "condition": predicted_condition
            })

        except ValueError as e:
            messages.error(request, "Invalid input values provided.")
            return render(request, "health_prediction/pcos.html")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return render(request, "health_prediction/pcos.html")


# Load the trained Obesity model
obesity_model_path = os.path.join(settings.BASE_DIR, "health_prediction", "models", "obesity_model.pkl")
with open(obesity_model_path, "rb") as file:
    obesity_model_data = pickle.load(file)

obesity_model = obesity_model_data["model"]
label_encoder = obesity_model_data["label_encoder"]

class ObesityView(View):
    def __init__(self):
        super().__init__()
        self.model = None
        self.label_encoder = None
        self._load_model()

    def _load_model(self):
        try:
            model_path = os.path.join(settings.BASE_DIR, "health_prediction", "models", "obesity_model.pkl")
            with open(model_path, "rb") as file:
                model_data = pickle.load(file)
            self.model = model_data["model"]
            self.label_encoder = model_data["label_encoder"]
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            self.model = None
            self.label_encoder = None

    def get(self, request):
        return render(request, "health_prediction/obesity.html")

    def post(self, request):
        # Ensure the form was actually submitted
        if request.method != "POST":
            return render(request, "health_prediction/pcos.html")  # Just show the page without validation

        if not self.model or not self.label_encoder:
            messages.error(request, "Sorry, the prediction service is currently unavailable.")
            return render(request, "health_prediction/obesity.html")

        try:
            # Get and validate user input
            features = []
            required_fields = [
                ("Gender", int), ("Age", int), ("Height", float),
                ("Weight", float), ("BMI", float), ("PhysicalActivityLevel", int)
            ]
            
            for field_name, field_type in required_fields:
                value = request.POST.get(field_name)
                if value is None:
                    messages.error(request, f"Missing required field: {field_name}")
                    return render(request, "health_prediction/obesity.html")
                try:
                    features.append(field_type(value))
                except ValueError:
                    messages.error(request, f"Invalid value for {field_name}")
                    return render(request, "health_prediction/obesity.html")

            # Make prediction
            input_features = np.array([features])
            prediction = self.model.predict(input_features)[0]
            predicted_condition = self.label_encoder.inverse_transform([prediction])[0]

            return render(request, "health_prediction/obesity_result.html", {
                "condition": predicted_condition
            })

        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return render(request, "health_prediction/obesity.html")


