from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.database import Base 



follows = Table(
    'follows',
    Base.metadata,
    Column('follower_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('followed_id', Integer, ForeignKey('users.id'), primary_key=True),
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    posts = relationship("Post", back_populates="author", lazy="select")
    comments = relationship("Comment", back_populates="author", lazy="select")
    following = relationship(
        "User",
        secondary="follows",
        primaryjoin="User.id == follows.c.follower_id",
        secondaryjoin="User.id == follows.c.followed_id",
        back_populates="followers",
        lazy="select",
    )
    followers = relationship(
        "User",
        secondary="follows",
        primaryjoin="User.id == follows.c.followed_id",
        secondaryjoin="User.id == follows.c.follower_id",
        back_populates="following",
        lazy="select",
    )

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"