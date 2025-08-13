import logging
from typing import Optional

from open_webui.internal.db import Base, get_db
from open_webui.models.charities import CharityModel
from pydantic import BaseModel, ConfigDict
from sqlalchemy import Boolean, Column, ForeignKey, Integer
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, relationship

logger = logging.getLogger(__name__)


class UserProfile(Base):

    __tablename__ = "user_profile"
    id = Column(Integer, primary_key=True)

    charity_id = Column(Integer, ForeignKey("charity.id"))
    charity = relationship("Charity")

    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates="profile")

    is_email_verified = Column(Boolean, default=False)


class UserProfileForm(BaseModel):
    user_id: str
    charity_id: Optional[int] = None


class UserProfileModel(BaseModel):
    charity: Optional[CharityModel] = None

    model_config = ConfigDict(from_attributes=True)

    def get_email_domain(self, user):
        if not user.email:
            return None

        email = user.email.strip().lower()

        try:
            domain = email.split("@")[1]
        except IndexError:
            return None
        return domain


class UserProfileTable:

    def assign_charity(
        self, db: Session, user_id: str, charity_id: Optional[int]
    ) -> Optional[UserProfile]:
        """
        Assign or clear a user's charity within an existing DB session.
        Does not commit — caller is responsible for commit/rollback.
        Returns ORM profile or None if user not found.
        """
        from open_webui.models.users import User

        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            return None

        profile = db.query(UserProfile).filter_by(user_id=user_id).first()
        if not profile:
            profile = UserProfile(user_id=user_id)
            db.add(profile)

        profile.charity_id = charity_id
        db.flush()
        return profile

    def set_user_charity(
        self, user_id: str, charity_id: Optional[int]
    ) -> Optional[UserProfileModel]:
        """
        Set the user's charity. Creates a UserProfile for the user if it does not exist.
        """

        db = None
        try:
            with get_db() as db:
                profile = self.assign_charity(db, user_id, charity_id)
                if profile is None:
                    return None

                db.commit()
                db.refresh(profile)
                return UserProfileModel.model_validate(profile)
        except SQLAlchemyError:
            if db is not None:
                db.rollback()
            return None


UserProfiles = UserProfileTable()
