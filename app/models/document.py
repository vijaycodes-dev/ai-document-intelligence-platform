from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)

    filename = Column(String(255), nullable=False)

    original_filename = Column(String(255), nullable=False)

    file_type = Column(String(50), nullable=False)

    file_size = Column(Integer, nullable=False)

    storage_path = Column(String(500), nullable=False)

    status = Column(
        String(50),
        default="uploaded",
        nullable=False,
    )
    
    processing_stage = Column(
        String(50),
        default="uploaded",
        nullable=False,
    )

    uploaded_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    metadata_entries = relationship(
        "DocumentMetadata",
        back_populates="document",
        cascade="all, delete-orphan",
    )
    
    chunks = relationship(
    "DocumentChunk",
    back_populates="document",
    cascade="all, delete-orphan",
    )
    
    processing_logs = relationship(
        "DocumentProcessingLog",
        back_populates="document",
        cascade="all, delete-orphan",
        order_by="DocumentProcessingLog.created_at",
    )