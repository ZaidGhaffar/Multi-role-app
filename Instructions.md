**Project Neurofy**
# 1. Project Overview
The client requires a web-based solution that enables employees to upload videos through a secure portal, which are then analyzed by an AI emotion detection system. The detected emotions (e.g., stressed, angry, happy, sad, etc.) will be presented as analytics in a dedicated HR dashboard.

The system consists of two main user types:
- Employee: Uploads videos through their company portal.
- HR (Human Resource Manager): Views analytics of employee-uploaded videos, including emotional states derived from AI predictions.

# 2. Functionality
**Employee Portal**
- Employee login & authentication (linked to their company).
- Upload video functionality (via signed URLs to GCS).
- uploaded videos (is_processed True or False).
- Secure storage of video metadata(Signed url) in the database (not the raw video).

**HR Dashboard**
- HR login & authentication (linked to their company).
- Dashboard displaying employee analytics (emotion distribution).
- Drill-down to see individual employee video results.

**AI Emotion Analysis**
- Deployed AI service to process uploaded videos.
- Predicts emotional states (e.g., anger, stress, happiness, etc.).
- Results stored in the database and mapped to corresponding employees.
- API endpoints to retrieve predictions for HR dashboard.

# 3. Tech Stack
- Backend: FastAPI (Python)
- Frontend: Next.js (React framework)
- Database: PostgreSQL + SQLAlchemy ORM
- Infrastructure & Storage: Google Cloud Platform (GCS for video storage, Compute Engine/Cloud Run for backend & AI model)
- Authentication: JWT-based authentication system
- AI Model: Pre-trained custom model (dummy placeholder initially, to be replaced later with full model deployment)


# 4. Important Information
- Each employee and HR user is linked to a Company (multi-tenancy architecture).
- Videos are not stored in the database, only on Google Cloud Storage. The database stores metadata (video URL, employee ID, timestamps, predictions) already desinged the Database.
- The AI model fetches videos securely from GCS using signed URLs.
- Predictions are always tied to the employee who uploaded the video for clear tracking.
- Careful database design has already been done to accommodate company-user relationships and predictions mapping.


5. What’s Done So Far
- ✅ Database schema designed & Build.
- ✅ Separate login & signup functionality for both Employees & HR.
- ✅ Portal/Dashboard segregation (Employee vs HR).
- ✅ Employees and HR linked through their respective companies.



### Phase 1 – Video Upload Integration  
- [✅] Implement API in FastAPI to **generate signed upload URL** (GCS) already implemented.  
- [ ] Frontend: Call API → get signed URL.  
- [ ] Frontend: Upload video directly to GCS.  
- [ ] Frontend: Notify FastAPI on upload completion (send metadata).  
- [ ] Backend: Store video metadata in PostgreSQL.  
- [ ] Update employee portal UI to show upload status/history.  

---

### Phase 2 – AI Model Integration  
- [ ]  Implement a dummy AI model function named EmotionModel that temporarily simulates predictions.This function will accept a video file path (from GCS signed URL).
It will return dummy top 3 emotions and scores in the form of a dictionary, for example:
predictions = {
  "happy": 0.78,
  "neutral": 0.15,
  "stressed": 0.07
}
Later, this placeholder will be replaced with the actual deployed AI model once it’s ready.
- [ ] Backend pipeline: Fetch video from GCS → call AI service(EmotionModel).  
- [ ] Compute derived fields: `top_emotion`, `top_score`.
- [ ] Store full prediction vector  fields in DB.  
- [ ] Update backend status is_processed=True→ processed.  
- [ ] Later: Replace dummy model with actual trained AI deployment i'll do that   

---

### Phase 3 – HR Dashboard Backend APIs  
- [ ] `GET /hr/dashboard/emotion-distribution` → for all emotions (defined in card) Stress,anxiety, fatigue, happiness, Neutral Anger, suprise.  
- [ ] `GET /hr/dashboard/emotion-pie-distribution` -> for pie charts. 
- [ ] `GET /hr/dashboard/emotion-trend` → for line/area chart.  
- [ ] `GET /hr/dashboard/emotion-histogram-distribution` -> for histgram charts. 
- [ ] `GET /hr/dashboard/Employee-department` → for cards with Total Employee & department.  
- [ ] `GET /hr/dashboard/summary` → for KPI cards.  
- [ ] `GET /hr/employees` → employee table with last prediction.  
- [ ] `GET /hr/employees/{employee_id}` → employee detail (history).  
in short I need the complete Backend for the hr dashboard connect it with frontend & test the all Api's
if something isn't mentioned feel free to add the code for it 
I just wants the working dashboard of hr with complete Backend & frontend integrated in it 
you can write code for Backend in hr_Dashboard folder import it & than use it in main.py file 

---

<!-- ### Phase 4 – HR Dashboard Frontend  
- [ ] Build **cards** (summary KPIs: total videos, active employees, avg stress, etc.).  
- [ ] Build **3 graphs** (emotion distribution, emotion trend, stress trend).  
- [ ] Build **employee table** with search, sort, pagination.  
- [ ] Build **employee detail view** (modal/page showing prediction history).   -->

---

### Phase 5 – Connect HR Frontend + Backend  
- [ ] Integrate all APIs with frontend components.  
- [ ] Ensure company-based data filtering (multi-tenancy).  
- [ ] Secure endpoints (JWT validation, role = HR).  

---

### Phase 6 – Testing & QA  
- [ ] Unit tests for backend APIs (FastAPI).  
- [ ] Integration tests (video upload → prediction → dashboard).  
- [ ] UI/UX testing for both portals.  
- [ ] Performance testing (large video uploads, concurrent users).  
- [ ] Security testing (signed URL expiry, access control).  
