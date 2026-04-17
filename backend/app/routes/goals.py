import uuid
from typing import List, Dict
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.core.database import get_db
from app.models.financial_goal import FinancialGoal
from app.routes.auth import get_current_user
from app.models.user import User
from app.core.db_config import get_category_breakdown, get_user_summary, get_user_range_summary

router = APIRouter(tags=["Goals"])

@router.get("/goals")
async def get_goals(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch all goals for the current user and calculate real-time progress.
    """
    stmt = select(FinancialGoal).where(FinancialGoal.user_id == current_user.id)
    result = await db.execute(stmt)
    goals = result.scalars().all()
    
    # Get current month numbers for progress
    now = datetime.now()
    month = now.month
    year = now.year
    
    # Fetch real spending breakdown
    # Since db_config uses user_id as string, we pass the UUID as string
    spending_data = get_category_breakdown(str(current_user.id), month=month, year=year)
    category_spent = {row['category']: float(row['spent']) for row in spending_data.get("breakdown", [])}
    
    # Fetch overall summary for savings goals
    summary = get_user_summary(str(current_user.id), month=month, year=year)
    total_income = summary.get("total_income", 0)
    total_expense = summary.get("total_expenses", 0)
    monthly_net_savings = total_income - total_expense

    enriched_goals = []
    for g in goals:
        current_progress = 0
        if g.goal_type == "SPENDING_LIMIT":
            current_progress = category_spent.get(g.category, 0)
        elif g.goal_type == "SAVINGS_GOAL":
            if g.period == "RANGE" and g.start_month and g.start_year and g.end_month and g.end_year:
                # Cumulative progress across specific range (and optional specific account)
                range_sum = get_user_range_summary(str(current_user.id), g.start_month, g.start_year, g.end_month, g.end_year, g.fi_data_id)
                current_progress = range_sum.get("net_savings", 0)
            elif g.fi_data_id:
                # Account-specific summary for current month
                acc_sum = get_user_summary(str(current_user.id), month, year, g.fi_data_id)
                current_progress = acc_sum.get("total_income", 0) - acc_sum.get("total_expenses", 0)
            else:
                # Default to current month net savings across all accounts
                current_progress = monthly_net_savings
            
        enriched_goals.append({
            "id": str(g.id),
            "goal_type": g.goal_type,
            "title": g.title,
            "fi_data_id": g.fi_data_id,
            "category": g.category,
            "target_amount": float(g.target_amount),
            "current_amount": current_progress,
            "period": g.period,
            "timeframe": {
                "start_month": g.start_month,
                "start_year": g.start_year,
                "end_month": g.end_month,
                "end_year": g.end_year
            } if g.period == "RANGE" else None,
            "status": g.status,
            "progress_percentage": min(100, (current_progress / float(g.target_amount) * 100)) if g.target_amount > 0 and current_progress > 0 else 0
        })
        
    return {"goals": enriched_goals}

@router.post("/goals")
async def create_goal(
    goal_data: Dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new financial goal (spending limit or savings target).
    """
    new_goal = FinancialGoal(
        user_id=current_user.id,
        goal_type=goal_data.get("goal_type"),
        title=goal_data.get("title"),
        fi_data_id=int(goal_data.get("fi_data_id")) if goal_data.get("fi_data_id") else None,
        category=goal_data.get("category"),
        target_amount=float(goal_data.get("target_amount")),
        period=goal_data.get("period", "MONTHLY"),
        start_month=int(goal_data.get("start_month")) if goal_data.get("start_month") else None,
        start_year=int(goal_data.get("start_year")) if goal_data.get("start_year") else None,
        end_month=int(goal_data.get("end_month")) if goal_data.get("end_month") else None,
        end_year=int(goal_data.get("end_year")) if goal_data.get("end_year") else None,
        status="ACTIVE"
    )
    db.add(new_goal)
    await db.commit()
    await db.refresh(new_goal)
    return {"status": "success", "goal_id": str(new_goal.id)}

@router.delete("/goals/{goal_id}")
async def delete_goal(
    goal_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Remove a goal.
    """
    try:
        goal_uuid = uuid.UUID(goal_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid goal ID format")
        
    stmt = delete(FinancialGoal).where(
        FinancialGoal.id == goal_uuid,
        FinancialGoal.user_id == current_user.id
    )
    result = await db.execute(stmt)
    await db.commit()
    
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Goal not found")
        
    return {"status": "success"}

@router.get("/goals/summary")
async def get_goals_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Simplified summary for the dashboard.
    """
    res = await get_goals(current_user, db)
    goals = res["goals"]
    
    on_track = [g for g in goals if g["goal_type"] == "SPENDING_LIMIT" and g["progress_percentage"] <= 100]
    exceeded = [g for g in goals if g["goal_type"] == "SPENDING_LIMIT" and g["progress_percentage"] > 100]
    savings = [g for g in goals if g["goal_type"] == "SAVINGS_GOAL"]
    
    return {
        "total_active": len(goals),
        "spending_on_track": len(on_track),
        "spending_exceeded": len(exceeded),
        "savings_goals_count": len(savings),
        "top_exceeded": exceeded[0] if exceeded else None
    }
