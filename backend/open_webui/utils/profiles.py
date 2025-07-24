import logging
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any

import boto3
from fastapi import Request
from itsdangerous import URLSafeTimedSerializer
from open_webui.env import WEBUI_NAME, WEBUI_SECRET_KEY
from open_webui.models.profiles import UserProfiles
from open_webui.models.users import Users

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "cast@devemail.org")
TO_EMAIL_ON_NEW_USER_SIGNUPS = os.environ.get(
    "TO_EMAIL_ON_NEW_USER_SIGNUPS", "steve@dev.ngo"
)
FRONTEND_BASE_URL = os.environ.get("FRONTEND_BASE_URL", None)
LOCAL = os.environ.get("LOCAL", False)


def get_email_verification_serializer() -> URLSafeTimedSerializer:
    """
    Returns a URLSafeTimedSerializer instance for generating and validating
    email verification tokens.
    """
    return URLSafeTimedSerializer(WEBUI_SECRET_KEY)


def send_verification_email(request: Request, email: str):
    serializer = get_email_verification_serializer()
    token = serializer.dumps(email, salt="email-confirmation-salt")

    if FRONTEND_BASE_URL:
        url = f"{FRONTEND_BASE_URL}verify?token={token}"
    else:
        url = f"{request.base_url}verify?token={token}"

    msg = MIMEMultipart()
    msg["Subject"] = "Verify your email"
    msg["From"] = DEFAULT_FROM_EMAIL
    msg["To"] = email
    body = MIMEText(f"Click the link {url} to verify your email!", "plain")
    msg.attach(body)

    if LOCAL:
        send_email(e_to=[email], config={}, mime_msg=msg, dryrun=True)
    else:
        send_email(e_to=[email], config={}, mime_msg=msg, dryrun=False)


def send_admin_email_notification(user):
    user_profile = user.profile
    msg = MIMEMultipart()
    msg["Subject"] = f"New user signup on {WEBUI_NAME}"
    msg["From"] = DEFAULT_FROM_EMAIL
    msg["To"] = TO_EMAIL_ON_NEW_USER_SIGNUPS
    if user.role == "user":
        status_text = f"A new user has registered on {WEBUI_NAME} and their account is already active."
    else:
        status_text = f"There is a new user registered on {WEBUI_NAME} that needs to be authorised."

    body = (
        f"{status_text}\n\n"
        f"Email: {user.email}\n"
        f"Name: {getattr(user, 'name', '')}\n"
        f"Charity: {getattr(getattr(user_profile, 'charity', None), 'name', '')}\n"
    )
    msg.attach(MIMEText(body))
    if LOCAL:
        send_email(
            e_to=[TO_EMAIL_ON_NEW_USER_SIGNUPS], config={}, mime_msg=msg, dryrun=True
        )
    else:
        send_email(
            e_to=[TO_EMAIL_ON_NEW_USER_SIGNUPS], config={}, mime_msg=msg, dryrun=True
        )


def send_email(
    e_to: list[str],
    mime_msg: MIMEMultipart,
    config: dict[str, Any],
    dryrun: bool = False,
) -> None:
    if dryrun:
        logger.info("Dryrun enabled, email notification content is below:")
        logger.info(mime_msg.as_string())
        return

    client = boto3.client(
        "sesv2", region_name=os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
    )

    send_email_kwargs = {}
    if os.environ.get("AWS_SES_FROM_ARN"):
        send_email_kwargs["FromEmailAddressIdentityArn"] = os.environ[
            "AWS_SES_FROM_ARN"
        ]
    if os.environ.get("AWS_SES_FEEDBACK_EMAIL"):
        send_email_kwargs["FeedbackForwardingEmailAddress"] = os.environ[
            "AWS_SES_FEEDBACK_EMAIL"
        ]
    if os.environ.get("AWS_SES_FEEDBACK_ARN"):
        send_email_kwargs["FeedbackForwardingEmailAddressIdentityArn"] = os.environ[
            "AWS_SES_FEEDBACK_ARN"
        ]

    client.send_email(
        FromEmailAddress=DEFAULT_FROM_EMAIL,
        Destination={
            "ToAddresses": e_to,
        },
        Content={
            "Raw": {
                "Data": mime_msg.as_bytes(),
            },
        },
        ConfigurationSetName=os.environ["AWS_SES_CONFIGURATION_SET_NAME"],
        **send_email_kwargs,
    )


def process_signup(request, user, charity):
    """
    Handles the signup processing workflow for a new user.

    This function performs the following steps:
        1. Creates or updates the user's profile and associates it with the specified charity.
        2. Refreshes and retrieves the updated user from the database (including the new profile).
        3. Sends a verification email to the user.
        4. Sends an admin notification email about the new signup.
        5. If both a charity and user profile exist, and the user's email domain matches the charity's website domain,
           updates the user's role to 'user'.
    """
    # Create user profile and set the charity
    user_profile = UserProfiles.update_or_create_user_profile(
        user.id, getattr(charity, "id", None), None
    )
    # Refresh user after creating profile
    user = Users.get_user_by_id(user.id)
    send_verification_email(request, user.email)
    send_admin_email_notification(user)

    if charity and user_profile:
        charity_domain = charity.get_website_domain()
        user_email_domain = user_profile.get_email_domain(user=user)
        if charity_domain is not None and user_email_domain is not None:
            if charity_domain == user_email_domain:
                user = Users.update_user_role_by_id(user.id, "user")

    return user, user_profile


def process_signin(user):
    """
    Handles user sign-in processing, including email verification if necessary.
    """
    user_profile = UserProfiles.get_userprofile_by_email(user.email)
    if not getattr(user_profile, "is_email_verified", False):
        # Resend verification email if user still not verified their email
        send_verification_email(user.email)
    return user_profile
