from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import requests

app = FastAPI()

# Static files and templates setup
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Container API URLs
specialty_predictor_url = "http://127.0.0.1:8080/predict"
doctor_recommendation_url = "http://127.0.0.1:8000/recommend/"


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the homepage."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/process", response_class=HTMLResponse)
async def process(request: Request, symptoms: str = Form(...)):
    """Process the input symptoms."""
    try:
        # Send symptoms to the Specialty Predictor container
        response = requests.post(
            specialty_predictor_url,
            json={"symptoms": symptoms},
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
        specialty_data = response.json()
        specialties = [spec["speciality"] for spec in specialty_data["top_specialists"]]

        # Send specialties to the Doctor Recommendation container
        doctor_response = requests.post(
            doctor_recommendation_url,
            json={"specialists": specialties},
            headers={"Content-Type": "application/json"},
        )
        doctor_response.raise_for_status()
        doctor_data = doctor_response.json()["recommendations"]

        return templates.TemplateResponse(
            "results.html",
            {
                "request": request,
                "symptoms": symptoms,
                "specialties": specialties,
                "recommendations": doctor_data,
            },
        )
    except Exception as e:
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "error": str(e)},
        )
