import os
import io
import json
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key="YOUR_API_KEY_HERE") # Replace with your key

app = FastAPI()

# This is vital for iPad browser testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/grade")
async def grade_exam(file: UploadFile = File(...), answer_key: str = Form(...)):
    # 1. Convert uploaded file to Image
    content = await file.read()
    img = Image.open(io.BytesIO(content))

    # 2. Call Gemini
    model = genai.GenerativeModel('gemini-2.0-flash')
    prompt = f"""
    Read the handwriting in this image. 
    The correct answer should be: {answer_key}
    Compare the handwritten text to the correct answer.
    If the meaning matches, give 5/5 marks. If not, give 0/5.
    Return only JSON: {{"text": "what you read", "score": "5/5", "status": "Correct"}}
    """
    
    response = model.generate_content([prompt, img])
    
    # 3. Clean and return JSON
    return json.loads(response.text.replace('```json', '').replace('```', ''))

if __name__ == "__main__":
    import uvicorn
    # 0.0.0.0 is required for GitHub Codespaces to see the traffic
    uvicorn.run(app, host="0.0.0.0", port=8000)
