# AI Face Recognition Photo Sharing - Build Plan

## Project Overview
Building an AI-powered photo sharing application for photography companies using face recognition and embeddings for fast search.

**Core Value:** Guest uploads selfie → See all photos they appear in from event → Download instantly

---

## Technical Architecture

### Tech Stack
- **Frontend:** React
- **Backend:** FastAPI (Python)
- **Face Recognition:** DeepFace/FaceNet (embeddings)
- **Database:** SQLite (local) → PostgreSQL/AWS (future)
- **Storage:** Local file system → AWS S3 (future)

### Data Flow
```
PHOTOGRAPHER WORKFLOW:
Event Photos → Batch Upload → Detect ALL faces in each photo
  ↓
Extract embedding for EACH face → Store in database
  ↓
Database: Photo + Embeddings + Face Location

GUEST WORKFLOW:
Guest uploads Selfie → Extract face embedding
  ↓
Vector similarity search in database
  ↓
Find ALL photos containing that person → Return list
  ↓
Guest downloads their photos
```

---

## Database Schema

### Tables
1. **events**
   - event_id (PK)
   - name
   - created_date
   - description

2. **photos**
   - photo_id (PK)
   - event_id (FK)
   - file_path
   - file_name
   - uploaded_date
   - file_size

3. **faces**
   - face_id (PK)
   - photo_id (FK)
   - embedding (vector/array)
   - face_location (x, y, w, h)
   - created_date

4. **guest_faces** (optional - for tagging)
   - guest_id (PK)
   - guest_name
   - embedding (from their selfie)
   - matched_faces (FK to faces table)

---

## Build Plan - Step by Step

### Phase 1: Backend Setup (FastAPI)

#### Step 1: Project Structure ✅
- [x] Create folder structure
- [x] Setup virtual environment
- [x] Install dependencies
- [x] Create requirements.txt

#### Step 2: Database Setup (NEXT)
- [ ] Create SQLAlchemy models for events, photos, faces
- [ ] Setup SQLite database connection
- [ ] Create database initialization script

#### Step 3: Face Embedding Service
- [ ] Install DeepFace
- [ ] Create face detection function (detect all faces in image)
- [ ] Create embedding extraction function (convert face to vector)
- [ ] Create vector similarity search function (find matching faces)

#### Step 4: FastAPI Endpoints
- [ ] POST `/api/events` - Create event
- [ ] POST `/api/photos/upload` - Upload event photos
- [ ] GET `/api/photos/{event_id}` - List event photos
- [ ] POST `/api/search` - Upload guest selfie + find matching photos
- [ ] GET `/api/download/{photo_id}` - Download photo
- [ ] GET `/api/guest-photos` - Get all photos for a guest

#### Step 5: Image Processing Pipeline
- [ ] Batch process event photos (detect faces, create embeddings)
- [ ] Store embeddings in database
- [ ] Handle errors and logging

### Phase 2: Frontend Setup (React)

#### Step 6: React Components
- [ ] Setup React project structure
- [ ] Event Upload Page (upload multiple photos)
- [ ] Gallery Page (show all event photos)
- [ ] Guest Search Page (upload selfie → search)
- [ ] Results Page (show matching photos)
- [ ] Download Page

#### Step 7: API Integration
- [ ] Setup axios/fetch for API calls
- [ ] Connect upload endpoints
- [ ] Connect search endpoint
- [ ] Connect download endpoint

### Phase 3: Integration & Testing

#### Step 8: End-to-End Testing
- [ ] Upload event photos
- [ ] Verify face detection
- [ ] Upload guest selfie
- [ ] Verify search results
- [ ] Test download

#### Step 9: UI/UX Polish
- [ ] Styling and responsive design
- [ ] Loading states
- [ ] Error handling
- [ ] User feedback messages

### Phase 4: Deployment Prep

#### Step 10: Local Deployment
- [ ] Docker setup (optional)
- [ ] Environment variables
- [ ] Performance optimization

---

## Key Libraries & Tools

```
FastAPI==0.104.0
uvicorn==0.24.0
SQLAlchemy==2.0.0
Pillow==10.0.0
opencv-python==4.8.0.76
deepface==0.0.81
numpy==1.24.0
scikit-learn==1.3.0
python-multipart==0.0.6
pydantic==1.10.12
python-dotenv==1.0.0
scipy==1.11.0
```

---

## Success Criteria

✅ Guest can upload event photos  
✅ System detects and embeds all faces  
✅ Guest uploads selfie  
✅ All matching photos returned  
✅ Guest can download their photos  
✅ Fast search (< 2 seconds for 1000 photos)  
✅ Accurate face matching (>90% accuracy)  

---

## Next Steps
1. ✅ Step 1 Complete: Project structure + dependencies
2. ⏳ Step 2: Database setup (SQLAlchemy models)
3. → Continue with remaining steps

**Current Status: Ready for Step 2!** 🚀
