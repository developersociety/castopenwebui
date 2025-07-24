import logging
from typing import Optional

from open_webui.env import SRC_LOG_LEVELS
from open_webui.internal.db import Base, get_db
from open_webui.models.charities import CharityModel
from pydantic import BaseModel, ConfigDict
from sqlalchemy import Boolean, Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["MODELS"])


class UserProfile(Base):

    __tablename__ = "user_profile"
    id = Column(Integer, primary_key=True)

    charity_id = Column(Integer, ForeignKey("charity.id"))
    charity = relationship("Charity")

    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates="profile")

    is_email_verified = Column(Boolean, default=False, nullable=False)


class UserProfileForm(BaseModel):
    user_id: str
    charity_id: Optional[int] = None
    is_email_verified: Optional[bool]


class UserProfileModel(BaseModel):
    charity: Optional[CharityModel] = None
    id: int
    is_email_verified: Optional[bool] = False

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
    def update_or_create_user_profile(
        self, user_id: str, charity_id: Optional[int], is_email_verified: Optional[bool]
    ) -> Optional[UserProfileModel]:
        """
        Set the user's charity. Creates a UserProfile for the user if it does not exist.
        """
        from open_webui.models.users import User

        try:
            with get_db() as db:
                # Check if user exists
                user = db.query(User).filter_by(id=user_id).first()
                if not user:
                    return False

                # Get or create the UserProfile
                user_profile = db.query(UserProfile).filter_by(user_id=user_id).first()
                if not user_profile:
                    user_profile = UserProfile(user_id=user_id)
                    db.add(user_profile)

                user_profile.charity_id = charity_id

                # Change is_email_verified
                if is_email_verified:
                    user_profile.is_email_verified = is_email_verified

                db.commit()
                db.refresh(user_profile)
                return UserProfileModel.model_validate(user_profile)
        except Exception as e:
            print("Error in update_or_create_user_profile:", e)
            return None

    def get_userprofile_by_email(self, email: str) -> Optional[UserProfileModel]:
        from open_webui.models.users import User  # prevent circular imports

        try:
            with get_db() as db:
                user_profile = (
                    db.query(UserProfile).join(User).filter(User.email == email).first()
                )
                return (
                    UserProfileModel.model_validate(user_profile)
                    if user_profile
                    else None
                )
        except Exception:
            return None

    def update_is_email_verified(
        self, id: int, is_email_verified: bool
    ) -> Optional[UserProfileModel]:
        try:
            with get_db() as db:
                db.query(UserProfile).filter_by(id=id).update(
                    {
                        "is_email_verified": is_email_verified,
                    }
                )
                db.commit()
                return self.get_user_profile_by_id(id=id)
        except Exception as e:
            log.exception(e)
            return None

    def get_user_profile_by_id(self, id: str) -> Optional[UserProfileModel]:
        try:
            with get_db() as db:
                user_profile = db.query(UserProfile).filter_by(id=id).first()
                return (
                    UserProfileModel.model_validate(user_profile)
                    if user_profile
                    else None
                )
        except Exception:
            return None


UserProfiles = UserProfileTable()
