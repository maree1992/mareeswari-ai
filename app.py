from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import zipfile
from io import BytesIO
from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image
import imagehash
import numpy as np
import base64

try:
    import face_recognition
    HAS_FACE_RECOGNITION = True
except ImportError:
    face_recognition = None
    HAS_FACE_RECOGNITION = False

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Mareeswari AI API",
    description="API for image processing and AI features",
    version="1.0.0"
)

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your React app URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    client = OpenAI(api_key=api_key)
else:
    client = None

VALID_IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp")


# Pydantic models
class ChatMessage(BaseModel):
    content: str


class ImageMatchRequest(BaseModel):
    method: str = "visual"  # "face" or "visual"
    threshold: float = 0.45
    max_matches: int = 10


# Helper functions
def is_valid_image(name: str) -> bool:
    return name.lower().endswith(VALID_IMAGE_EXTS)


def load_image_from_bytes(data: bytes) -> Image.Image:
    return Image.open(BytesIO(data)).convert("RGB")


def image_to_base64(image: Image.Image) -> str:
    """Convert PIL Image to base64 string"""
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return img_str


# Health and Status endpoints
@app.get("/")
async def root():
    return {"message": "Mareeswari AI API is running"}


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "has_face_recognition": HAS_FACE_RECOGNITION,
        "has_openai": client is not None
    }


# OpenAI Chat endpoints
@app.post("/api/chat")
async def chat(message: ChatMessage):
    """Send a message to OpenAI and get a response"""
    if not client:
        raise HTTPException(status_code=500, detail="OpenAI client not configured")
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": message.content}],
            max_tokens=500,
        )
        
        return {
            "success": True,
            "response": response.choices[0].message.content.strip()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/test-openai")
async def test_openai():
    """Test OpenAI connectivity"""
    if not client:
        raise HTTPException(status_code=500, detail="OpenAI client not configured")
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say hello"}],
            max_tokens=10,
        )
        return {
            "success": True,
            "message": "OpenAI connectivity test succeeded",
            "response": response.choices[0].message.content.strip()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI connectivity test failed: {str(e)}")


# Image matching endpoints
@app.post("/api/match-faces")
async def match_faces(
    reference: UploadFile = File(...),
    threshold: float = 0.45,
    max_matches: int = 10
):
    """Match faces in uploaded image against a reference image"""
    if not HAS_FACE_RECOGNITION:
        raise HTTPException(status_code=400, detail="Face recognition not available")
    
    try:
        # Read reference image
        reference_data = await reference.read()
        reference_image = load_image_from_bytes(reference_data)
        reference_array = np.array(reference_image)
        
        # Extract face encodings from reference
        reference_encodings = face_recognition.face_encodings(reference_array)
        if not reference_encodings:
            raise HTTPException(status_code=400, detail="No face found in reference image")
        
        return {
            "success": True,
            "message": "Face reference processed successfully",
            "faces_detected": len(reference_encodings)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/match-visual-similarity")
async def match_visual_similarity(
    reference: UploadFile = File(...),
    threshold: float = 20,
    max_matches: int = 10
):
    """Match images based on visual similarity using image hashing"""
    try:
        # Read reference image
        reference_data = await reference.read()
        reference_image = load_image_from_bytes(reference_data)
        
        # Compute image hashes
        phash = imagehash.phash(reference_image)
        dhash = imagehash.dhash(reference_image)
        
        return {
            "success": True,
            "message": "Visual similarity reference processed",
            "phash": str(phash),
            "dhash": str(dhash)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/process-candidates")
async def process_candidates(
    reference: UploadFile = File(...),
    candidates: list[UploadFile] = File(...),
    method: str = "visual",
    threshold: float = 20
):
    """Process multiple candidate images against a reference image"""
    try:
        # Read reference image
        reference_data = await reference.read()
        reference_image = load_image_from_bytes(reference_data)
        
        matches = []
        
        if method == "face" and HAS_FACE_RECOGNITION:
            # Face recognition method
            reference_array = np.array(reference_image)
            reference_encodings = face_recognition.face_encodings(reference_array)
            
            if not reference_encodings:
                raise HTTPException(status_code=400, detail="No face in reference image")
            
            reference_encoding = reference_encodings[0]
            
            for candidate_file in candidates:
                try:
                    candidate_data = await candidate_file.read()
                    candidate_image = load_image_from_bytes(candidate_data)
                    candidate_array = np.array(candidate_image)
                    candidate_encodings = face_recognition.face_encodings(candidate_array)
                    
                    if candidate_encodings:
                        distances = face_recognition.face_distance(
                            candidate_encodings, 
                            reference_encoding
                        )
                        min_distance = float(min(distances))
                        matches.append({
                            "name": candidate_file.filename,
                            "distance": min_distance,
                            "image": image_to_base64(candidate_image)
                        })
                except Exception as e:
                    print(f"Error processing {candidate_file.filename}: {e}")
        
        else:
            # Visual similarity method
            reference_phash = imagehash.phash(reference_image)
            reference_dhash = imagehash.dhash(reference_image)
            
            for candidate_file in candidates:
                try:
                    candidate_data = await candidate_file.read()
                    candidate_image = load_image_from_bytes(candidate_data)
                    candidate_phash = imagehash.phash(candidate_image)
                    candidate_dhash = imagehash.dhash(candidate_image)
                    
                    phash_distance = reference_phash - candidate_phash
                    dhash_distance = reference_dhash - candidate_dhash
                    distance = round((phash_distance + dhash_distance) / 2, 2)
                    
                    matches.append({
                        "name": candidate_file.filename,
                        "distance": distance,
                        "image": image_to_base64(candidate_image)
                    })
                except Exception as e:
                    print(f"Error processing {candidate_file.filename}: {e}")
        
        # Sort by distance and filter
        matches.sort(key=lambda x: x["distance"])
        matched_images = [m for m in matches if m["distance"] <= threshold][:10]
        
        return {
            "success": True,
            "method": method,
            "total_candidates": len(candidates),
            "matches_found": len(matched_images),
            "matches": matched_images
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
