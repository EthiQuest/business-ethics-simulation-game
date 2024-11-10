from fastapi import HTTPException, Security, Depends
from fastapi.security import OAuth2AuthorizationCodeBearer, SecurityScopes
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, Dict
import logging

from ...models.auth import TokenData, User
from ...services.db_service import DBService
from ...core.cache.cache_service import CacheService
from ...config import Settings, get_settings

logger = logging.getLogger(__name__)

class AuthHandler:
    """Handles authentication and authorization logic"""
    
    def __init__(self, settings: Settings):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        self.oauth2_scheme = OAuth2AuthorizationCodeBearer(
            authorizationUrl="auth/authorize",
            tokenUrl="auth/token"
        )

    async def create_access_token(
        self,
        data: dict,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
            
        to_encode.update({"exp": expire})
        
        try:
            encoded_jwt = jwt.encode(
                to_encode,
                self.secret_key,
                algorithm=self.algorithm
            )
            return encoded_jwt
        except Exception as e:
            logger.error(f"Error creating access token: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Could not create access token"
            )

    async def verify_token(
        self,
        token: str,
        security_scopes: SecurityScopes,
        db: DBService,
        cache: CacheService
    ) -> TokenData:
        """Verify JWT token and return token data"""
        if not token:
            raise HTTPException(
                status_code=401,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )

        try:
            # Check token blacklist in cache
            is_blacklisted = await cache.get(f"blacklist:{token}")
            if is_blacklisted:
                raise HTTPException(
                    status_code=401,
                    detail="Token has been revoked"
                )

            # Decode token
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            
            user_id: str = payload.get("sub")
            if user_id is None:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid token"
                )

            # Verify scopes
            token_scopes = payload.get("scopes", [])
            for scope in security_scopes.scopes:
                if scope not in token_scopes:
                    raise HTTPException(
                        status_code=403,
                        detail="Not enough permissions"
                    )

            return TokenData(
                user_id=user_id,
                scopes=token_scopes
            )

        except JWTError as e:
            logger.error(f"JWT verification error: {str(e)}")
            raise HTTPException(
                status_code=401,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    async def get_current_user(
        self,
        security_scopes: SecurityScopes,
        token: str = Depends(oauth2_scheme),
        db: DBService = Depends(DBService.get_instance),
        cache: CacheService = Depends(CacheService.get_instance)
    ) -> User:
        """Get current authenticated user"""
        token_data = await self.verify_token(token, security_scopes, db, cache)
        
        # Check cache first
        cached_user = await cache.get(f"user:{token_data.user_id}")
        if cached_user:
            return User(**cached_user)

        # Get from database
        user = await db.get_user(token_data.user_id)
        if user is None:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        # Cache user data
        await cache.set(
            f"user:{token_data.user_id}",
            user.dict(),
            ttl=3600  # 1 hour cache
        )

        return user

    async def revoke_token(
        self,
        token: str,
        cache: CacheService
    ) -> None:
        """Revoke a token by adding it to blacklist"""
        try:
            # Decode token to get expiration
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            
            # Calculate TTL (time until token expires)
            exp = datetime.fromtimestamp(payload['exp'])
            ttl = (exp - datetime.utcnow()).total_seconds()
            
            if ttl > 0:
                # Add to blacklist with TTL
                await cache.set(
                    f"blacklist:{token}",
                    True,
                    ttl=int(ttl)
                )
        except Exception as e:
            logger.error(f"Error revoking token: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Could not revoke token"
            )

class PermissionChecker:
    """Checks user permissions for specific operations"""

    @staticmethod
    def check_player_access(user_id: str, player_id: str) -> bool:
        """Check if user has access to player data"""
        return user_id == player_id

    @staticmethod
    def check_admin_access(user: User) -> bool:
        """Check if user has admin privileges"""
        return 'admin' in user.roles

# Dependencies for route protection
auth_handler = AuthHandler(get_settings())

async def get_current_active_user(
    security_scopes: SecurityScopes,
    current_user: User = Depends(auth_handler.get_current_user)
) -> User:
    """Dependency for getting current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=400,
            detail="Inactive user"
        )
    return current_user

async def get_current_admin(
    current_user: User = Security(
        get_current_active_user,
        scopes=["admin"]
    )
) -> User:
    """Dependency for admin-only routes"""
    if not PermissionChecker.check_admin_access(current_user):
        raise HTTPException(
            status_code=403,
            detail="Admin privileges required"
        )
    return current_user

def check_player_access(
    player_id: str,
    current_user: User = Depends(get_current_active_user)
) -> bool:
    """Dependency for checking player access"""
    if not PermissionChecker.check_player_access(
        current_user.id,
        player_id
    ):
        raise HTTPException(
            status_code=403,
            detail="Access denied to player data"
        )
    return True

# Example protected route decorator
def require_active_user(scopes: Optional[List[str]] = None):
    """Decorator for routes requiring authenticated active user"""
    if scopes is None:
        scopes = []
        
    return Security(
        get_current_active_user,
        scopes=scopes
    )

# Usage example in routes:
"""
@router.get("/protected")
async def protected_route(
    user: User = Depends(require_active_user(['read:data']))
):
    return {"message": f"Hello {user.username}"}
"""