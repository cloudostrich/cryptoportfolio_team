from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Annotated, Optional
from ..models.schemas import ThesisCreate, ThesisResponse, VoteRequest
from ..db import queries
from .auth import get_current_user, get_optional_user

router = APIRouter(prefix="/api/theses", tags=["theses"])

@router.post("", response_model=ThesisResponse)
def create_thesis(thesis: ThesisCreate, current_user: Annotated[dict, Depends(get_current_user)]):
    try:
        new_thesis = queries.create_thesis(
            user_id=current_user["id"],
            coin_id=thesis.coin_id,
            coin_symbol=thesis.coin_symbol,
            title=thesis.title,
            content=thesis.content,
            sentiment=thesis.sentiment,
            target_price=thesis.target_price,
            time_horizon=thesis.time_horizon
        )
        # Add username for response
        new_thesis["username"] = current_user["username"]
        new_thesis["votes_count"] = 0
        new_thesis["user_vote"] = None
        return new_thesis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("", response_model=List[ThesisResponse])
def get_theses(current_user: Annotated[Optional[dict], Depends(get_optional_user)]):
    user_id = current_user["id"] if current_user else None
    theses = queries.get_all_theses(current_user_id=user_id)
    return theses

@router.post("/{thesis_id}/vote")
def vote_thesis(thesis_id: str, vote: VoteRequest, current_user: Annotated[dict, Depends(get_current_user)]):
    success = queries.vote_thesis(thesis_id, current_user["id"], vote.vote_type)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to record vote")
    return {"status": "success"}
