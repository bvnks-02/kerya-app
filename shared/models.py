"""
Shared database models for Kerya App microservices.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from sqlalchemy import (
    Boolean, Column, DateTime, Decimal as SQLDecimal, Enum as SQLEnum,
    ForeignKey, Integer, String, Text, Index, CheckConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class UserType(str, Enum):
    """User type enumeration."""
    CLIENT = "client"
    HOST = "host"


class PropertyType(str, Enum):
    """Property type enumeration."""
    STUDIO = "studio"
    F1 = "f1"
    F2 = "f2"
    F3 = "f3"
    F4 = "f4"
    F5 = "f5"
    VILLA = "villa"
    APARTMENT = "apartment"
    HOUSE = "house"


class BookingStatus(str, Enum):
    """Booking status enumeration."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    REJECTED = "rejected"


class PaymentStatus(str, Enum):
    """Payment status enumeration."""
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


class NotificationType(str, Enum):
    """Notification type enumeration."""
    BOOKING_CONFIRMED = "booking_confirmed"
    BOOKING_CANCELLED = "booking_cancelled"
    NEW_MESSAGE = "new_message"
    NEW_REVIEW = "new_review"
    PAYMENT_RECEIVED = "payment_received"
    SYSTEM_UPDATE = "system_update"


class User(Base):
    """User model for authentication and profile management."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(20), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    user_type = Column(SQLEnum(UserType), nullable=False, default=UserType.CLIENT)
    is_verified = Column(Boolean, default=False, nullable=False)
    profile_image = Column(String(500), nullable=True)
    rating = Column(SQLDecimal(3, 2), default=0.00, nullable=False)
    points = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    properties = relationship("Property", back_populates="host", cascade="all, delete-orphan")
    bookings_as_guest = relationship("Booking", back_populates="guest", foreign_keys="Booking.guest_id")
    reviews = relationship("Review", back_populates="user", cascade="all, delete-orphan")
    posts = relationship("Post", back_populates="user", cascade="all, delete-orphan")
    sent_messages = relationship("Message", back_populates="sender", foreign_keys="Message.sender_id")
    received_messages = relationship("Message", back_populates="receiver", foreign_keys="Message.receiver_id")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("idx_users_email", "email"),
        Index("idx_users_phone", "phone"),
        Index("idx_users_user_type", "user_type"),
        Index("idx_users_rating", "rating"),
        CheckConstraint("rating >= 0 AND rating <= 5", name="check_rating_range"),
        CheckConstraint("points >= 0", name="check_points_positive"),
    )


class Property(Base):
    """Property model for rental listings."""
    
    __tablename__ = "properties"
    
    id = Column(Integer, primary_key=True, index=True)
    host_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    property_type = Column(SQLEnum(PropertyType), nullable=False)
    price_per_night = Column(SQLDecimal(10, 2), nullable=False)
    wilaya = Column(String(100), nullable=False)
    address = Column(Text, nullable=False)
    latitude = Column(SQLDecimal(10, 8), nullable=True)
    longitude = Column(SQLDecimal(11, 8), nullable=True)
    max_guests = Column(Integer, nullable=False)
    bedrooms = Column(Integer, nullable=False)
    bathrooms = Column(Integer, nullable=False)
    is_available = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    host = relationship("User", back_populates="properties")
    bookings = relationship("Booking", back_populates="property", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="property", cascade="all, delete-orphan")
    images = relationship("PropertyImage", back_populates="property", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("idx_properties_host_id", "host_id"),
        Index("idx_properties_wilaya", "wilaya"),
        Index("idx_properties_price", "price_per_night"),
        Index("idx_properties_type", "property_type"),
        Index("idx_properties_location", "latitude", "longitude"),
        Index("idx_properties_available", "is_available"),
        CheckConstraint("price_per_night > 0", name="check_positive_price"),
        CheckConstraint("max_guests > 0", name="check_positive_guests"),
        CheckConstraint("bedrooms >= 0", name="check_non_negative_bedrooms"),
        CheckConstraint("bathrooms >= 0", name="check_non_negative_bathrooms"),
    )


class PropertyImage(Base):
    """Property image model for storing image URLs."""
    
    __tablename__ = "property_images"
    
    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    image_url = Column(String(500), nullable=False)
    is_primary = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    property = relationship("Property", back_populates="images")
    
    # Indexes
    __table_args__ = (
        Index("idx_property_images_property_id", "property_id"),
        Index("idx_property_images_primary", "is_primary"),
    )


class Booking(Base):
    """Booking model for reservations."""
    
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    guest_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    check_in_date = Column(DateTime(timezone=True), nullable=False)
    check_out_date = Column(DateTime(timezone=True), nullable=False)
    guests_count = Column(Integer, nullable=False)
    total_price = Column(SQLDecimal(10, 2), nullable=False)
    status = Column(SQLEnum(BookingStatus), default=BookingStatus.PENDING, nullable=False)
    payment_status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    special_requests = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    guest = relationship("User", back_populates="bookings_as_guest")
    property = relationship("Property", back_populates="bookings")
    review = relationship("Review", back_populates="booking", uselist=False, cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("idx_bookings_guest_id", "guest_id"),
        Index("idx_bookings_property_id", "property_id"),
        Index("idx_bookings_dates", "check_in_date", "check_out_date"),
        Index("idx_bookings_status", "status"),
        Index("idx_bookings_payment_status", "payment_status"),
        CheckConstraint("check_out_date > check_in_date", name="check_valid_dates"),
        CheckConstraint("guests_count > 0", name="check_positive_guests"),
        CheckConstraint("total_price > 0", name="check_positive_total"),
    )


class Review(Base):
    """Review model for property ratings and comments."""
    
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    booking = relationship("Booking", back_populates="review")
    user = relationship("User", back_populates="reviews")
    property = relationship("Property", back_populates="reviews")
    
    # Indexes
    __table_args__ = (
        Index("idx_reviews_booking_id", "booking_id"),
        Index("idx_reviews_user_id", "user_id"),
        Index("idx_reviews_property_id", "property_id"),
        Index("idx_reviews_rating", "rating"),
        CheckConstraint("rating >= 1 AND rating <= 5", name="check_rating_range"),
    )


class Post(Base):
    """Post model for client-driven posting system."""
    
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    budget_min = Column(SQLDecimal(10, 2), nullable=False)
    budget_max = Column(SQLDecimal(10, 2), nullable=False)
    location = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    points_cost = Column(Integer, default=10, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="posts")
    
    # Indexes
    __table_args__ = (
        Index("idx_posts_user_id", "user_id"),
        Index("idx_posts_location", "location"),
        Index("idx_posts_budget", "budget_min", "budget_max"),
        Index("idx_posts_active", "is_active"),
        CheckConstraint("budget_min > 0", name="check_positive_budget_min"),
        CheckConstraint("budget_max >= budget_min", name="check_budget_range"),
        CheckConstraint("points_cost >= 0", name="check_positive_points_cost"),
    )


class Message(Base):
    """Message model for user-to-user communication."""
    
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    read_status = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    sender = relationship("User", back_populates="sent_messages", foreign_keys=[sender_id])
    receiver = relationship("User", back_populates="received_messages", foreign_keys=[receiver_id])
    
    # Indexes
    __table_args__ = (
        Index("idx_messages_sender_id", "sender_id"),
        Index("idx_messages_receiver_id", "receiver_id"),
        Index("idx_messages_read_status", "read_status"),
        Index("idx_messages_created_at", "created_at"),
    )


class Notification(Base):
    """Notification model for system notifications."""
    
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(SQLEnum(NotificationType), nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    read_status = Column(Boolean, default=False, nullable=False)
    data = Column(Text, nullable=True)  # JSON data for additional context
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    
    # Indexes
    __table_args__ = (
        Index("idx_notifications_user_id", "user_id"),
        Index("idx_notifications_type", "type"),
        Index("idx_notifications_read_status", "read_status"),
        Index("idx_notifications_created_at", "created_at"),
    ) 