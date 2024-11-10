from passlib.context import CryptContext
from datetime import datetime, timedelta
import secrets
import string
import logging
import jwt
from typing import Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from ..config import Settings, get_settings

# Initialize password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Initialize logger
logger = logging.getLogger(__name__)

class SecurityUtils:
    """Security utility functions for the application"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.password_length = 12
        self.token_length = 32
        self.reset_token_expire_hours = 24
        
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        try:
            return pwd_context.hash(password)
        except Exception as e:
            logger.error(f"Password hashing error: {str(e)}")
            raise ValueError("Password hashing failed")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            logger.error(f"Password verification error: {str(e)}")
            return False

    def generate_password(self) -> str:
        """Generate a secure random password"""
        try:
            # Define character sets
            lowercase = string.ascii_lowercase
            uppercase = string.ascii_uppercase
            digits = string.digits
            symbols = "!@#$%^&*"
            
            # Ensure at least one of each type
            password = [
                secrets.choice(lowercase),
                secrets.choice(uppercase),
                secrets.choice(digits),
                secrets.choice(symbols)
            ]
            
            # Fill remaining length with random characters
            all_characters = lowercase + uppercase + digits + symbols
            password.extend(
                secrets.choice(all_characters)
                for _ in range(self.password_length - len(password))
            )
            
            # Shuffle the password
            secrets.SystemRandom().shuffle(password)
            
            return ''.join(password)
        except Exception as e:
            logger.error(f"Password generation error: {str(e)}")
            raise ValueError("Password generation failed")

    def generate_token(self, length: Optional[int] = None) -> str:
        """Generate a secure random token"""
        try:
            token_length = length or self.token_length
            return secrets.token_urlsafe(token_length)
        except Exception as e:
            logger.error(f"Token generation error: {str(e)}")
            raise ValueError("Token generation failed")

    def generate_reset_token(self, user_id: str) -> str:
        """Generate a password reset token"""
        try:
            # Create token payload
            payload = {
                "user_id": user_id,
                "exp": datetime.utcnow() + timedelta(hours=self.reset_token_expire_hours),
                "type": "password_reset"
            }
            
            # Generate JWT token
            token = jwt.encode(
                payload,
                self.settings.SECRET_KEY,
                algorithm=self.settings.ALGORITHM
            )
            
            return token
        except Exception as e:
            logger.error(f"Reset token generation error: {str(e)}")
            raise ValueError("Reset token generation failed")

    def verify_reset_token(self, token: str) -> Optional[str]:
        """Verify a password reset token and return user_id if valid"""
        try:
            # Decode JWT token
            payload = jwt.decode(
                token,
                self.settings.SECRET_KEY,
                algorithms=[self.settings.ALGORITHM]
            )
            
            # Verify token type and expiration
            if payload.get("type") != "password_reset":
                return None
                
            return payload.get("user_id")
        except jwt.ExpiredSignatureError:
            logger.warning("Expired reset token used")
            return None
        except jwt.JWTError as e:
            logger.error(f"Reset token verification error: {str(e)}")
            return None

    async def send_password_reset_email(
        self,
        user_email: str,
        reset_token: str
    ) -> bool:
        """Send password reset email"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.settings.EMAIL_FROM
            msg['To'] = user_email
            msg['Subject'] = "Password Reset Request"
            
            # Create reset link
            reset_link = f"{self.settings.FRONTEND_URL}/reset-password?token={reset_token}"
            
            # Create email body
            body = f"""
            Hello,

            You have requested to reset your password. Please click the link below to reset it:

            {reset_link}

            This link will expire in {self.reset_token_expire_hours} hours.

            If you did not request this reset, please ignore this email.

            Best regards,
            The EthiQuest Team
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(
                self.settings.SMTP_SERVER,
                self.settings.SMTP_PORT
            ) as server:
                server.starttls()
                server.login(
                    self.settings.SMTP_USERNAME,
                    self.settings.SMTP_PASSWORD
                )
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending reset email: {str(e)}")
            return False

    def validate_password_strength(self, password: str) -> tuple[bool, str]:
        """
        Validate password strength
        Returns (is_valid, message)
        """
        try:
            if len(password) < 8:
                return False, "Password must be at least 8 characters long"
                
            if not any(c.isupper() for c in password):
                return False, "Password must contain at least one uppercase letter"
                
            if not any(c.islower() for c in password):
                return False, "Password must contain at least one lowercase letter"
                
            if not any(c.isdigit() for c in password):
                return False, "Password must contain at least one number"
                
            if not any(c in string.punctuation for c in password):
                return False, "Password must contain at least one special character"
                
            return True, "Password meets strength requirements"
            
        except Exception as e:
            logger.error(f"Password validation error: {str(e)}")
            return False, "Password validation failed"

    def sanitize_token(self, token: str) -> str:
        """Sanitize token input"""
        try:
            # Remove any whitespace or special characters
            return ''.join(
                c for c in token
                if c in string.ascii_letters + string.digits + '-_.'
            )
        except Exception as e:
            logger.error(f"Token sanitization error: {str(e)}")
            raise ValueError("Token sanitization failed")

# Create global instance
security_utils = SecurityUtils(get_settings())

# Export convenience functions
hash_password = security_utils.hash_password
verify_password = security_utils.verify_password
generate_password = security_utils.generate_password
generate_token = security_utils.generate_token
generate_reset_token = security_utils.generate_reset_token
verify_reset_token = security_utils.verify_reset_token
send_password_reset_email = security_utils.send_password_reset_email
validate_password_strength = security_utils.validate_password_strength
sanitize_token = security_utils.sanitize_token