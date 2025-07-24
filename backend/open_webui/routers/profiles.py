import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from itsdangerous import BadSignature, SignatureExpired
from open_webui.env import SRC_LOG_LEVELS
from open_webui.models.profiles import UserProfileModel, UserProfiles
from open_webui.utils.profiles import get_email_verification_serializer

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["MODELS"])

router = APIRouter()


@router.get(
    "/verify-email", name="verify-email", response_model=Optional[UserProfileModel]
)
async def verify_email(token: str):
    serializer = get_email_verification_serializer()
    try:
        # 1 week expiry
        email = serializer.loads(
            token, salt="email-confirmation-salt", max_age=60 * 60 * 24 * 7
        )
    except SignatureExpired:
        raise HTTPException(status_code=400, detail="Verification link expired.")
    except BadSignature:
        raise HTTPException(status_code=400, detail="Invalid verification token.")
    user_profile = UserProfiles.get_userprofile_by_email(email)
    if not user_profile:
        raise HTTPException(status_code=404, detail="User not found")
    user_profile = UserProfiles.update_is_email_verified(
        id=int(user_profile.id), is_email_verified=True
    )
    return user_profile
