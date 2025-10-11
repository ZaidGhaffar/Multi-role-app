from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from auth.dependencies import get_current_user, get_db
from Database.database import Users, Video, Prediction, Department


router = APIRouter()


STANDARD_EMOTIONS = [
    "stress",
    "anxiety",
    "fatigue",
    "happiness",
    "neutral",
    "anger",
    "surprise",
]


SYNONYM_TO_STANDARD = {
    # model -> standard mapping
    "stressed": "stress",
    "stress": "stress",
    "anxious": "anxiety",
    "anxiety": "anxiety",
    "tired": "fatigue",
    "fatigue": "fatigue",
    "happy": "happiness",
    "happiness": "happiness",
    "neutral": "neutral",
    "angry": "anger",
    "anger": "anger",
    "surprised": "surprise",
    "surprise": "surprise",
}


def assert_hr(user: Users) -> None:
    if user.role != "hr":
        raise HTTPException(status_code=403, detail="HR role required")


def map_emotion(label: str) -> Optional[str]:
    if not label:
        return None
    key = label.strip().lower()
    return SYNONYM_TO_STANDARD.get(key)


def get_company_user_ids(db: Session, company_id: str) -> List[str]:
    return [u.user_id for u in db.query(Users).filter(Users.company_id == company_id).all()]


@router.get("/hr/dashboard/emotion-distribution")
def emotion_distribution(db: Session = Depends(get_db), user: Users = Depends(get_current_user)):
    assert_hr(user)
    user_ids = get_company_user_ids(db, user.company_id)
    if not user_ids:
        return {"distribution": {k: 0 for k in STANDARD_EMOTIONS}}

    # Count occurrences weighted by score across company videos
    counts: Dict[str, float] = {k: 0.0 for k in STANDARD_EMOTIONS}

    q = (
        db.query(Prediction)
        .join(Video, Video.video_id == Prediction.video_id)
        .filter(Video.user_id.in_(user_ids))
    )
    for p in q:
        std = map_emotion(p.emotion_label)
        if std in counts:
            counts[std] += float(p.score)

    # Convert to ints where appropriate but keep numeric
    return {"distribution": counts}


@router.get("/hr/dashboard/emotion-pie-distribution")
def emotion_pie_distribution(db: Session = Depends(get_db), user: Users = Depends(get_current_user)):
    assert_hr(user)
    result = emotion_distribution(db=db, user=user)
    dist: Dict[str, float] = result["distribution"]
    total = sum(dist.values()) or 1.0
    pie = {k: (v / total) for k, v in dist.items()}
    return {"pie": pie}


@router.get("/hr/dashboard/emotion-trend")
def emotion_trend(
    days: int = Query(30, ge=1, le=180),
    db: Session = Depends(get_db),
    user: Users = Depends(get_current_user),
):
    assert_hr(user)
    user_ids = get_company_user_ids(db, user.company_id)
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=days - 1)

    # Initialize structure: date -> emotion -> sum, count
    date_keys = [start_date + timedelta(days=i) for i in range(days)]
    sums: Dict[str, Dict[str, float]] = {d.isoformat(): {e: 0.0 for e in STANDARD_EMOTIONS} for d in date_keys}
    counts: Dict[str, Dict[str, int]] = {d.isoformat(): {e: 0 for e in STANDARD_EMOTIONS} for d in date_keys}

    q = (
        db.query(Prediction, Video)
        .join(Video, Video.video_id == Prediction.video_id)
        .filter(Video.user_id.in_(user_ids))
        .filter(Prediction.created_at >= datetime.combine(start_date, datetime.min.time()))
        .filter(Prediction.created_at <= datetime.combine(end_date, datetime.max.time()))
    )

    for p, v in q:
        std = map_emotion(p.emotion_label)
        if std not in STANDARD_EMOTIONS:
            continue
        dkey = p.created_at.date().isoformat()
        if dkey in sums:
            sums[dkey][std] += float(p.score)
            counts[dkey][std] += 1

    series = []
    for d in date_keys:
        key = d.isoformat()
        entry = {"date": key}
        for e in STANDARD_EMOTIONS:
            c = counts[key][e]
            entry[e] = (sums[key][e] / c) if c else 0.0
        series.append(entry)

    return {"series": series}


@router.get("/hr/dashboard/emotion-histogram-distribution")
def emotion_histogram_distribution(
    emotion: str = Query("stress"),
    bins: int = Query(10, ge=2, le=20),
    db: Session = Depends(get_db),
    user: Users = Depends(get_current_user),
):
    assert_hr(user)
    std = map_emotion(emotion) or emotion.strip().lower()
    if std not in STANDARD_EMOTIONS:
        raise HTTPException(status_code=400, detail="Unsupported emotion")

    user_ids = get_company_user_ids(db, user.company_id)
    scores: List[float] = []
    q = (
        db.query(Prediction)
        .join(Video, Video.video_id == Prediction.video_id)
        .filter(Video.user_id.in_(user_ids))
    )
    for p in q:
        mapped = map_emotion(p.emotion_label)
        if mapped == std:
            scores.append(float(p.score))

    # Build histogram
    step = 1.0 / bins
    counts = [0 for _ in range(bins)]
    for s in scores:
        idx = int(min(bins - 1, max(0, s // step)))
        counts[int(idx)] += 1

    ranges = [
        {"from": round(i * step, 3), "to": round((i + 1) * step, 3), "count": counts[i]}
        for i in range(bins)
    ]

    return {"emotion": std, "histogram": ranges}


@router.get("/hr/dashboard/employee-department")
def employee_department(db: Session = Depends(get_db), user: Users = Depends(get_current_user)):
    assert_hr(user)
    # Department data not modeled; return totals only for now
    total_employees = db.query(Users).filter(Users.company_id == user.company_id).count(),
    departments = db.query(Department).order_by(Department.name.asc()).all()
    return {
        "total_employees": total_employees,
        "departments": departments,
    }


@router.get("/hr/dashboard/summary")
def dashboard_summary(db: Session = Depends(get_db), user: Users = Depends(get_current_user)):
    assert_hr(user)
    user_ids = get_company_user_ids(db, user.company_id)
    total_videos = db.query(Video).filter(Video.user_id.in_(user_ids)).count()
    processed_videos = db.query(Video).filter(Video.user_id.in_(user_ids), Video.is_processed == True).count()

    # Active employees: those with at least one video
    active_employee_ids = (
        db.query(Video.user_id)
        .filter(Video.user_id.in_(user_ids))
        .distinct()
        .all()
    )
    active_employees = len(active_employee_ids)

    # Average stress score
    stress_scores: List[float] = []
    q = (
        db.query(Prediction)
        .join(Video, Video.video_id == Prediction.video_id)
        .filter(Video.user_id.in_(user_ids))
    )
    for p in q:
        std = map_emotion(p.emotion_label)
        if std == "stress":
            stress_scores.append(float(p.score))

    avg_stress = (sum(stress_scores) / len(stress_scores)) if stress_scores else 0.0

    return {
        "total_videos": total_videos,
        "processed_videos": processed_videos,
        "active_employees": active_employees,
        "avg_stress": avg_stress,
    }


# @router.get("/hr/employees")
# def list_employees(
#     page: int = Query(1, ge=1),
#     page_size: int = Query(10, ge=1, le=100),
#     db: Session = Depends(get_db),
#     user: Users = Depends(get_current_user),
# ):
#     assert_hr(user)
#     q = db.query(Users).filter(Users.company_id == user.company_id)
#     total = q.count()
#     employees = q.order_by(Users.username.asc()).offset((page - 1) * page_size).limit(page_size).all()

#     # Get last prediction per employee (by latest prediction created_at for their latest processed video)
#     items = []
#     for emp in employees:
#         last_video = (
#             db.query(Video)
#             .filter(Video.user_id == emp.user_id, Video.is_processed == True)
#             .order_by(Video.upload_timestamp.desc())
#             .first()
#         )
#         last_pred = None
#         top_emotion = None
#         top_score = None
#         if last_video:
#             preds = db.query(Prediction).filter(Prediction.video_id == last_video.video_id).all()
#             if preds:
#                 pred_map = {p.emotion_label: float(p.score) for p in preds}
#                 # map keys to standard
#                 std_map: Dict[str, float] = {}
#                 for k, v in pred_map.items():
#                     m = map_emotion(k)
#                     if m:
#                         std_map[m] = v
#                 if std_map:
#                     top_emotion = max(std_map, key=std_map.get)
#                     top_score = std_map[top_emotion]
#                 last_pred = std_map

#         items.append(
#             {
#                 "user_id": emp.user_id,
#                 "username": emp.username,
#                 "last_video_id": last_video.video_id if last_video else None,
#                 "last_prediction": last_pred,
#                 "top_emotion": top_emotion,
#                 "top_score": top_score,
#             }
#         )

#     return {"total": total, "page": page, "page_size": page_size, "items": items}


@router.get("/hr/employees/{employee_id}")
def employee_detail(employee_id: str, db: Session = Depends(get_db), user: Users = Depends(get_current_user)):
    assert_hr(user)
    emp = db.query(Users).filter(Users.user_id == employee_id, Users.company_id == user.company_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    videos = (
        db.query(Video)
        .filter(Video.user_id == emp.user_id)
        .order_by(Video.upload_timestamp.desc())
        .all()
    )

    history = []
    for v in videos:
        preds = db.query(Prediction).filter(Prediction.video_id == v.video_id).all()
        pred_map: Dict[str, float] = {}
        for p in preds:
            m = map_emotion(p.emotion_label)
            if m:
                pred_map[m] = float(p.score)
        top_emotion = max(pred_map, key=pred_map.get) if pred_map else None
        top_score = pred_map.get(top_emotion) if top_emotion else None
        history.append(
            {
                "video_id": v.video_id,
                "uploaded_at": v.upload_timestamp.isoformat() if v.upload_timestamp else None,
                "is_processed": v.is_processed,
                "predictions": pred_map,
                "top_emotion": top_emotion,
                "top_score": top_score,
            }
        )

    return {
        "user_id": emp.user_id,
        "username": emp.username,
        "history": history,
    }


##############################
@router.get("/hr/employees")
def list_employees(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    user: Users = Depends(get_current_user),
):
    # ✅ Ensure user is HR
    assert_hr(user)

    # ✅ Get only employees (non-HR) from same company
    q = (
        db.query(Users)
        .filter(
            Users.company_id == user.company_id,
            Users.role != "hr"  # exclude HRs
        )
    )

    total = q.count()
    employees = (
        q.order_by(Users.username.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    items = []
    for emp in employees:
        last_video = (
            db.query(Video)
            .filter(Video.user_id == emp.user_id, Video.is_processed == True)
            .order_by(Video.upload_timestamp.desc())
            .first()
        )

        last_pred = None
        top_emotion = None
        top_score = None

        if last_video:
            preds = db.query(Prediction).filter(Prediction.video_id == last_video.video_id).all()
            if preds:
                pred_map = {p.emotion_label: float(p.score) for p in preds}
                std_map = {}
                for k, v in pred_map.items():
                    m = map_emotion(k)
                    if m:
                        std_map[m] = v
                if std_map:
                    top_emotion = max(std_map, key=std_map.get)
                    top_score = std_map[top_emotion]
                last_pred = std_map

        items.append(
            {
                "user_id": emp.user_id,
                "username": emp.username,
                "email": emp.email,
                "role": emp.role,
                "last_video_id": last_video.video_id if last_video else None,
                "last_prediction": last_pred,
                "top_emotion": top_emotion,
                "top_score": top_score,
            }
        )

    return {"total": total, "page": page, "page_size": page_size, "items": items}
