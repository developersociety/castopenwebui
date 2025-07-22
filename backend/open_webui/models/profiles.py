from typing import Optional

from open_webui.internal.db import Base, get_db
from sqlalchemy.orm import relationship

from pydantic import BaseModel, ConfigDict, field_validator
from open_webui.internal.db import Base

from sqlalchemy import Column, ForeignKey, Integer


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
    id: Optional[int] = None
    user_id: str
    charity_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class UserProfileTable:
    def add(
        self,
        form_data: UserProfileForm,
    ) -> Optional[UserProfileModel]:
        with get_db() as db:
            user_profile = UserProfile(**form_data.model_dump(exclude_none=True))
            db.add(user_profile)
            db.commit()
            db.refresh(user_profile)  # Get DB-generated fields like id
            return UserProfileModel.model_validate(user_profile)


UserProfiles = UserProfileTable()
