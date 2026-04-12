import os
import io
import json
import google.generativeai as genai
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image

# 1. Setup API Key - PUT YOUR KEY INSIDE THE QUOTES
genai.configure(api_key="")

app = FastAPI()

# Vital for iPad browser testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ROUTE 1: SHOW THE WEBSITE ---
@app.get("/", response_class=HTMLResponse)
async def read_index():
    try:
        with open("index.html", "r") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>Error: index.html not found!</h1><p>Make sure your HTML file is named exactly index.html</p>"

# --- ROUTE 2: PROCESS THE EXAM ---
@app.post("/grade")
async def grade_exam(file: UploadFile = File(...), answer_key: str = Form(...)):
    try:
        # 1. Convert uploaded file to Image
        content = await file.read()
        img = Image.open(io.BytesIO(content))

        # 2. Call Gemini
        model = genai.GenerativeModel('gemini-2.0-flash')
        prompt = f"""
        Read the handwriting in this image. 
        The correct answer should be: {answer_key}
        Compare the handwritten text to the correct answer.
        If the meaning matches the core concept, give 5/5 marks. If not, give 0/5.
        Return only JSON format: {{"text": "the transcription", "score": "5/5", "status": "Correct"}}
        """
        
        response = model.generate_content([prompt, img])
        
        # 3. Clean and return JSON
        # This part removes markdown formatting if Gemini adds it
        clean_json = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(clean_json)
    
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    # 0.0.0.0 is required for GitHub Codespaces on iPad
    uvicorn.run(app, host="0.0.0.0", port=8000)
