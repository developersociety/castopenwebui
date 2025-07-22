from typing import Optional

from open_webui.internal.db import Base, get_db
from open_webui.models.charities import CharityModel
from pydantic import BaseModel, ConfigDict
from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship


class UserProfile(Base):
    __tablename__ = "user_profile"
    id = Column(Integer, primary_key=True)

    charity_id = Column(Integer, ForeignKey("charity.id"))
    charity = relationship("Charity")

    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates="profile")


class UserProfileForm(BaseModel):
    user_id: str
    charity_id: Optional[int] = None


class UserProfileModel(BaseModel):
    charity: Optional[CharityModel] = None

    model_config = ConfigDict(from_attributes=True)


class UserProfileTable:
    def set_user_charity(self, user_id: str, charity_id: Optional[int]) -> bool:
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
                db.commit()
                return True
        except Exception as e:
            print("Error in set_user_charity:", e)
            return False


UserProfiles = UserProfileTable()
