2. Functionality
Employee Portal

Employee login & authentication (linked to their company).
Upload video functionality (via signed URLs to GCS).
uploaded videos (is_processed True or False).
Secure storage of video metadata(Signed url) in the database (not the raw video).
HR Dashboard

HR login & authentication (linked to their company).
Dashboard displaying employee analytics (emotion distribution).
Drill-down to see individual employee video results.
AI Emotion Analysis

Deployed AI service to process uploaded videos.
Predicts emotional states (e.g., anger, stress, happiness, etc.).
Results stored in the database and mapped to corresponding employees.
API endpoints to retrieve predictions for HR dashboard.
