import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Numeric, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class FinancialGoal(Base):
    __tablename__ = "financial_goals"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Optional account-specific tracking (NULL = Consolidated)
    fi_data_id: Mapped[int | None] = mapped_column(nullable=True)
    
    # SPENDING_LIMIT or SAVINGS_GOAL
    goal_type: Mapped[str] = mapped_column(String(30), nullable=False)
    
    # Optional name for the goal
    title: Mapped[str | None] = mapped_column(String(100), nullable=True)
    
    # e.g., "Food & Dining" (null for savings goals)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    
    # The target amount (limit or savings target)
    target_amount: Mapped[float] = mapped_column(Numeric(20, 2), nullable=False)
    
    # MONTHLY or YEARLY or RANGE
    period: Mapped[str] = mapped_column(String(20), default="MONTHLY")
    
    # Custom timeframe fields (for period="RANGE" or multi-month goals)
    start_month: Mapped[int | None] = mapped_column(nullable=True)
    start_year: Mapped[int | None] = mapped_column(nullable=True)
    end_month: Mapped[int | None] = mapped_column(nullable=True)
    end_year: Mapped[int | None] = mapped_column(nullable=True)
    
    # Active/Completed/etc.
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self):
        return f"<FinancialGoal {self.goal_type} - {self.category or 'Global'} - {self.target_amount}>"
