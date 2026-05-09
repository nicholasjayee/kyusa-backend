import os
import django
from datetime import datetime, timedelta, timezone, date, time
from asgiref.sync import sync_to_async


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from fastapi import FastAPI, Depends, HTTPException, status, Response, Cookie
from fastapi import UploadFile, File, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, validator
from typing import List, Optional,Any

from django.contrib.auth.hashers import check_password
from django.db.models import Q
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from django.core.mail import send_mail
from django.conf import settings
from django.core.exceptions import ValidationError



from apps.core.models import (
    User, Department, Notification, Role,
    ClientProfile, Favorite,
    ProviderProfile, Availability, AvailabilityException,
    ServiceCategory, Service,
    Booking, Review,
    PaymentTransaction, PaymentMethod, CommissionRule,
    ProviderEarnings, Payout,
    Dispute, DisputeEvidence, AuditLog, SystemSetting,
    RefreshToken
)



# JWT settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-me")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


# Pydantic schemas
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[str] = "client"

    @validator('role')
    def validate_role(cls, v):
        if v not in ['client', 'provider']:
            raise ValueError('Role must be "client" or "provider"')
        return v

class UserOut(BaseModel):
    id: str
    email: str
    username: str
    first_name: str
    last_name: str
    role: str
    is_active: bool

class Token(BaseModel):
    access_token: str
    token_type: str

class DepartmentCreate(BaseModel):
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    is_active: bool = True

class ServiceCategoryCreate(BaseModel):
    department_id: str
    name: str
    description: Optional[str] = None
    is_active: bool = True

class ClientProfileCreate(BaseModel):
    phone_number: str
    preferred_language: Optional[str] = "en"
    notification_preferences: Optional[dict] = None

class BookingAction(BaseModel):
    notes: Optional[str] = None


class AvailabilityCreate(BaseModel):
    day_of_week: int  # 0=Monday .. 6=Sunday
    start_time: str   # "09:00"
    end_time: str     # "17:00"
    is_off: bool = False
    max_bookings_per_day: Optional[int] = 10

class AvailabilityExceptionCreate(BaseModel):
    date: date
    is_off: bool = False
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    reason: Optional[str] = None

class ReviewCreate(BaseModel):
    rating: int  # 1-5
    comment: Optional[str] = None

class ProviderApprovalAction(BaseModel):
    approved: bool
    notes: Optional[str] = None

class PayoutRequest(BaseModel):
    amount: float
    destination: str   # e.g., bank account, mobile money number
    notes: Optional[str] = None

class FavoriteResponse(BaseModel):
    id: str
    service_id: str
    service_name: str
    service_base_price: float
    created_at: datetime

class SettingUpdate(BaseModel):
    value: Any
    value_type: Optional[str] = 'string'
    description: Optional[str] = ''
    is_public: bool = False

    model_config = {'arbitrary_types_allowed': True}


class DisputeCreate(BaseModel):
    reason: str
    booking_id: str

class DisputeResolve(BaseModel):
    status: str   # 'resolved_closed' or 'resolved_refund'
    resolution_notes: Optional[str] = None

class DisputeResolve(BaseModel):
    status: str   # 'resolved_closed' or 'resolved_refund'
    resolution_notes: Optional[str] = None

# Helper functions (sync_to_async wrapped)
@sync_to_async
def get_user_by_email(email: str):
    try:
        return User.objects.get(email=email)
    except User.DoesNotExist:
        return None

@sync_to_async
def get_user_by_id(user_id: str):
    try:
        return User.objects.get(id=user_id, is_active=True)
    except User.DoesNotExist:
        return None

@sync_to_async
def create_user(email: str, username: str, password: str, first_name: str, last_name: str, role: str):
    return User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        role=role,
        is_active=True
    )

def _authenticate_user_sync(email: str, password: str):
    try:
        user = User.objects.get(email=email)
        if check_password(password, user.password):
            return user
        return None
    except User.DoesNotExist:
        return None

authenticate_user = sync_to_async(_authenticate_user_sync)

@sync_to_async
def check_username_exists(username: str):
    return User.objects.filter(username=username).exists()

# JWT token creation (sync, fine)
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

# Dependency to get current user (async)
async def get_current_user(access_token: Optional[str] = Depends(oauth2_scheme)):
    if access_token is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = decode_token(access_token)
    if payload is None or payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = await get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=401, detail="Account is inactive")
    return user

from django.core.asgi import get_asgi_application

from fastapi.staticfiles import StaticFiles

# FastAPI app
app = FastAPI(title="Kyusa API", version="1.0")

# Mount Static Files (Served directly by FastAPI for efficiency)
if os.path.exists("staticfiles"):
    app.mount("/static", StaticFiles(directory="staticfiles"), name="static")

# Mount Django
django_app = get_asgi_application()
app.mount("/_/admin", django_app)

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:8000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Role-based dependency
def require_role(allowed_roles: list):
    async def role_checker(current_user: User = Depends(get_current_user)):
        # Allow Django superusers to access any endpoint
        if current_user.is_superuser:
            return current_user
        if current_user.role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return role_checker


# helper to get active, approved provider
@sync_to_async
def get_provider_profile(user):
    try:
        return ProviderProfile.objects.get(user=user)
    except ProviderProfile.DoesNotExist:
        return None

async def get_active_provider(current_user: User = Depends(get_current_user)):
    if current_user.role not in ["provider", "admin"]:
        raise HTTPException(status_code=403, detail="Only providers can perform this action")
    provider = await get_provider_profile(current_user)
    if not provider:
        raise HTTPException(status_code=400, detail="Provider profile not found")
    if not provider.is_approved:
        raise HTTPException(status_code=403, detail="Your provider account is pending approval")
    return provider

# Public endpoints
@app.get("/api/health")
def health():
    return {"status": "ok", "models_count": 22}

@app.post("/api/auth/signup", response_model=UserOut)
async def signup(user_data: UserCreate):
    if await get_user_by_email(user_data.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    if await check_username_exists(user_data.username):
        raise HTTPException(status_code=400, detail="Username already taken")
    
    user = await create_user(
        email=user_data.email,
        username=user_data.username,
        password=user_data.password,
        first_name=user_data.first_name or "",
        last_name=user_data.last_name or "",
        role=user_data.role
    )
    return UserOut(
        id=user.id,
        email=user.email,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
        is_active=user.is_active
    )

@app.post("/api/auth/login")
async def login(response: Response, form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        path="/",
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/auth/refresh")
async def refresh_token(response: Response, refresh_token: Optional[str] = Cookie(None)):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")
    payload = decode_token(refresh_token)
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    user_id = payload.get("sub")
    user = await get_user_by_id(user_id) if user_id else None
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    new_access_token = create_access_token(data={"sub": str(user.id)})
    new_refresh_token = create_refresh_token(data={"sub": str(user.id)})
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        path="/"
    )
    return {"access_token": new_access_token, "token_type": "bearer"}

@app.post("/api/auth/logout")
async def logout(response: Response, current_user: User = Depends(get_current_user)):
    response.delete_cookie("refresh_token", path="/")
    return {"message": "Logged out"}

@app.get("/api/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return UserOut(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        role=current_user.role,
        is_active=current_user.is_active
    )


@app.get("/api/provider-only")
async def provider_only(current_user: User = Depends(require_role(["provider", "admin"]))):
    return {"message": f"Welcome provider {current_user.email}"}

@app.get("/api/admin-only")
async def admin_only(current_user: User = Depends(require_role(["admin"]))):
    return {"message": f"Welcome admin {current_user.email}"}




@app.get("/api/services")
async def list_services(category: str = None, search: str = None, min_price: float = None, max_price: float = None):
    @sync_to_async
    def get_services():
        qs = Service.objects.filter(is_active=True)
        if category:
            qs = qs.filter(category_id=category)
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(description__icontains=search))
        if min_price is not None:
            qs = qs.filter(base_price__gte=min_price)
        if max_price is not None:
            qs = qs.filter(base_price__lte=max_price)
        return list(qs.values(
            "id", "name", "description", "base_price", "duration_minutes",
            "requires_prepayment", "provider__business_name", "category__name"
        ))
    services = await get_services()
    return {"count": len(services), "results": services}


# provider endpoints
class ServiceCreate(BaseModel):
    category_id: str
    name: str
    description: str
    base_price: float
    duration_minutes: Optional[int] = None
    requires_prepayment: bool = False
    cancellation_policy_hours: int = 24

@app.post("/api/provider/services")
async def create_service(service_data: ServiceCreate, provider = Depends(get_active_provider)):
    category = await sync_to_async(lambda: ServiceCategory.objects.get(id=service_data.category_id, is_active=True))()
    service = await sync_to_async(Service.objects.create)(
        provider=provider,
        category=category,
        name=service_data.name,
        description=service_data.description,
        base_price=service_data.base_price,
        duration_minutes=service_data.duration_minutes,
        requires_prepayment=service_data.requires_prepayment,
        cancellation_policy_hours=service_data.cancellation_policy_hours,
    )
    return {"id": service.id, "name": service.name, "message": "Service created"}

@app.get("/api/services/{service_id}")
async def service_detail(service_id: str):
    try:
        service = await sync_to_async(Service.objects.select_related('provider', 'category').get)(id=service_id, is_active=True)
        return {
            "id": service.id,
            "name": service.name,
            "description": service.description,
            "base_price": service.base_price,
            "duration_minutes": service.duration_minutes,
            "requires_prepayment": service.requires_prepayment,
            "cancellation_policy_hours": service.cancellation_policy_hours,
            "provider": {
                "id": service.provider.id,
                "business_name": service.provider.business_name,
                "rating_avg": service.provider.rating_avg,
                "total_reviews": service.provider.total_reviews,
            },
            "category": {
                "id": service.category.id,
                "name": service.category.name,
            }
        }
    except Service.DoesNotExist:
        raise HTTPException(status_code=404, detail="Service not found")


class ProviderProfileCreate(BaseModel):
    business_name: str
    business_registration_number: Optional[str] = None
    phone_number: str
    address: Optional[str] = None
    profile_picture_url: Optional[str] = None
    commission_rate: Optional[float] = None

@app.post("/api/provider/onboarding")
async def create_provider_profile(
    profile_data: ProviderProfileCreate,
    current_user: User = Depends(get_current_user)
):
    if current_user.role != 'provider':
        raise HTTPException(status_code=403, detail="Only providers can create a provider profile")
    
    existing = await get_provider_profile(current_user)
    if existing:
        raise HTTPException(status_code=400, detail="Provider profile already exists")
    
    @sync_to_async
    def create():
        return ProviderProfile.objects.create(
            user=current_user,
            business_name=profile_data.business_name,
            business_registration_number=profile_data.business_registration_number,
            phone_number=profile_data.phone_number,
            address=profile_data.address,
            profile_picture=profile_data.profile_picture_url,
            commission_rate=profile_data.commission_rate,
            is_approved=False,
            rating_avg=0.00,
            total_reviews=0
        )
    provider_profile = await create()
    return {
        "id": provider_profile.id,
        "business_name": provider_profile.business_name,
        "is_approved": provider_profile.is_approved,
        "message": "Provider profile created, pending approval"
    }


# Admin: Department management
@app.post("/api/admin/departments")
async def create_department(data: DepartmentCreate, admin: User = Depends(require_role(["admin"]))):
    @sync_to_async
    def create():
        return Department.objects.create(
            name=data.name,
            description=data.description,
            icon=data.icon,
            is_active=data.is_active
        )
    dept = await create()
    return {"id": dept.id, "name": dept.name, "is_active": dept.is_active}

@app.get("/api/admin/departments")
async def list_departments(admin: User = Depends(require_role(["admin"]))):
    @sync_to_async
    def get():
        return list(Department.objects.values("id", "name", "description", "icon", "is_active", "created_at"))
    return await get()

# Admin: ServiceCategory management
@app.post("/api/admin/service-categories")
async def create_service_category(data: ServiceCategoryCreate, admin: User = Depends(require_role(["admin"]))):
    try:
        dept = await sync_to_async(Department.objects.get)(id=data.department_id, is_active=True)
    except Department.DoesNotExist:
        raise HTTPException(status_code=404, detail="Department not found")
    
    @sync_to_async
    def create():
        return ServiceCategory.objects.create(
            department=dept,
            name=data.name,
            description=data.description,
            is_active=data.is_active
        )
    category = await create()
    return {"id": category.id, "name": category.name, "department_id": category.department.id, "is_active": category.is_active}

@app.get("/api/admin/service-categories")
async def list_service_categories(admin: User = Depends(require_role(["admin"]))):
    @sync_to_async
    def get():
        return list(ServiceCategory.objects.select_related('department').values(
            "id", "name", "description", "is_active", "department__id", "department__name"
        ))
    return await get()




# client apis

class BookingCreate(BaseModel):
    service_id: str
    booking_date: date
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    special_requests: Optional[str] = None
    metadata: Optional[dict] = None

@app.post("/api/bookings")
async def create_booking(booking_data: BookingCreate, current_user: User = Depends(get_current_user)):
    if current_user.role != 'client':
        raise HTTPException(status_code=403, detail="Only clients can create bookings")
    
    try:
        client = await sync_to_async(ClientProfile.objects.get)(user=current_user)
    except ClientProfile.DoesNotExist:
        raise HTTPException(status_code=400, detail="Client profile not found")
    
    try:
        service = await sync_to_async(Service.objects.select_related('provider').get)(id=booking_data.service_id, is_active=True)
    except Service.DoesNotExist:
        raise HTTPException(status_code=404, detail="Service not found")
    
    total_amount = service.base_price
    metadata_val = booking_data.metadata if booking_data.metadata is not None else {}
    
    @sync_to_async
    def create():
        return Booking.objects.create(
            client=client,
            service=service,
            provider=service.provider,
            booking_date=booking_data.booking_date,
            start_time=booking_data.start_time,
            end_time=booking_data.end_time,
            status='pending',
            special_requests=booking_data.special_requests,
            total_amount=total_amount,
            commission_amount=0,
            metadata=metadata_val,
        )
    booking = await create()
    # Send email to provider
    provider_email = service.provider.user.email
    await send_email_async(
        subject="New Booking Request",
        message=f"Dear {service.provider.business_name},\n\nA new booking has been created for your service '{service.name}'.\nBooking ID: {booking.id}\nClient: {current_user.email}\nDate: {booking.booking_date}\n\nPlease log in to accept or reject.",
        recipient_list=[provider_email]
    )
    return {"id": booking.id, "status": booking.status, "message": "Booking created, pending provider acceptance"}


@app.post("/api/client/onboarding")
async def create_client_profile(
    profile_data: ClientProfileCreate,
    current_user: User = Depends(get_current_user)
):
    if current_user.role != 'client':
        raise HTTPException(status_code=403, detail="Only clients can create a client profile")
    
    existing = await sync_to_async(ClientProfile.objects.filter(user=current_user).exists)()
    if existing:
        raise HTTPException(status_code=400, detail="Client profile already exists")
    
    @sync_to_async
    def create():
        return ClientProfile.objects.create(
            user=current_user,
            phone_number=profile_data.phone_number,
            preferred_language=profile_data.preferred_language or "en",
            notification_preferences=profile_data.notification_preferences or {"email": True, "sms": False}
        )
    client_profile = await create()
    return {
        "id": client_profile.id,
        "phone_number": client_profile.phone_number,
        "preferred_language": client_profile.preferred_language,
        "message": "Client profile created"
    }


@app.get("/api/bookings")
async def list_client_bookings(status: Optional[str] = None, current_user: User = Depends(get_current_user)):
    if current_user.role != 'client':
        raise HTTPException(status_code=403, detail="Only clients can view their bookings this way")
    
    try:
        client = await sync_to_async(ClientProfile.objects.get)(user=current_user)
    except ClientProfile.DoesNotExist:
        raise HTTPException(status_code=400, detail="Client profile not found")
    
    @sync_to_async
    def get():
        qs = Booking.objects.filter(client=client).select_related('provider', 'service')
        if status:
            qs = qs.filter(status=status)
        return list(qs.values(
            "id", "booking_date", "start_time", "end_time", "status", "total_amount",
            "special_requests", "provider__business_name", "service__name"
        ))
    bookings = await get()
    return {"count": len(bookings), "bookings": bookings}


@app.post("/api/provider/bookings/{booking_id}/accept")
async def accept_booking(booking_id: str, action: BookingAction = None, provider: ProviderProfile = Depends(get_active_provider)):
    try:
        booking = await sync_to_async(Booking.objects.select_related('client', 'service').get)(id=booking_id, provider=provider)
    except Booking.DoesNotExist:
        raise HTTPException(status_code=404, detail="Booking not found for this provider")
    
    if booking.status != 'pending':
        raise HTTPException(status_code=400, detail=f"Booking cannot be accepted (current status: {booking.status})")
    
    @sync_to_async
    def update():
        booking.status = 'accepted'
        if action and action.notes:
            booking.provider_notes = action.notes
        booking.save()
        return booking
    await update()
    client_email = booking.client.user.email
    await send_email_async(
        subject="Booking Accepted",
        message=f"Dear {booking.client.user.first_name},\n\nYour booking for '{booking.service.name}' on {booking.booking_date} has been accepted by the provider.\nYou can now arrange details with them.\n\nThank you.",
        recipient_list=[client_email]
    )
    return {"id": booking.id, "status": "accepted", "message": "Booking accepted"}

@app.post("/api/provider/bookings/{booking_id}/reject")
async def reject_booking(booking_id: str, action: BookingAction = None, provider: ProviderProfile = Depends(get_active_provider)):
    try:
        booking = await sync_to_async(Booking.objects.get)(id=booking_id, provider=provider)
    except Booking.DoesNotExist:
        raise HTTPException(status_code=404, detail="Booking not found for this provider")
    
    if booking.status != 'pending':
        raise HTTPException(status_code=400, detail=f"Booking cannot be rejected (current status: {booking.status})")
    
    @sync_to_async
    def update():
        booking.status = 'rejected'
        if action and action.notes:
            booking.provider_notes = action.notes
        booking.save()
        return booking
    await update()
    return {"id": booking.id, "status": "rejected", "message": "Booking rejected"}

@app.get("/api/provider/bookings")
async def list_provider_bookings(status: Optional[str] = None, provider: ProviderProfile = Depends(get_active_provider)):
    @sync_to_async
    def get():
        qs = Booking.objects.filter(provider=provider).select_related('client__user', 'service')
        if status:
            qs = qs.filter(status=status)
        return list(qs.values(
            "id", "booking_date", "start_time", "end_time", "status", "total_amount",
            "special_requests", "client__user__email", "service__name"
        ))
    bookings = await get()
    return {"count": len(bookings), "bookings": bookings}

# This endpoint replaces the entire weekly schedule for the provider. The client should send an array of 7 entries (one for each day of the week) with the desired availability settings. The server will delete any existing schedule and create new entries based on the provided data.
@app.post("/api/provider/availability")
async def set_availability(
    availability_data: List[AvailabilityCreate],
    provider: ProviderProfile = Depends(get_active_provider)
):
    @sync_to_async
    def update():
        # Delete existing schedule for this provider
        provider.availabilities.all().delete()
        # Create new entries
        for avail in availability_data:
            Availability.objects.create(
                provider=provider,
                day_of_week=avail.day_of_week,
                start_time=avail.start_time,
                end_time=avail.end_time,
                is_off=avail.is_off,
                max_bookings_per_day=avail.max_bookings_per_day
            )
        return True
    await update()
    return {"message": "Availability schedule updated"}


@app.post("/api/provider/availability/exceptions")
async def add_exception(
    exception_data: AvailabilityExceptionCreate,
    provider: ProviderProfile = Depends(get_active_provider)
):
    @sync_to_async
    def create():
        # Upsert: if exists for that date, update; else create
        obj, created = AvailabilityException.objects.update_or_create(
            provider=provider,
            date=exception_data.date,
            defaults={
                "is_off": exception_data.is_off,
                "start_time": exception_data.start_time,
                "end_time": exception_data.end_time,
                "reason": exception_data.reason,
            }
        )
        return obj
    exc = await create()
    return {"id": exc.id, "date": exc.date, "is_off": exc.is_off, "message": "Exception saved"}

@app.get("/api/provider/availability/exceptions")
async def list_exceptions(provider: ProviderProfile = Depends(get_active_provider)):
    @sync_to_async
    def get():
        return list(provider.availability_exceptions.values(
            "id", "date", "is_off", "start_time", "end_time", "reason"
        ))
    exceptions = await get()
    return {"exceptions": exceptions}



@app.delete("/api/provider/availability/exceptions/{exception_id}")
async def delete_exception(exception_id: str, provider: ProviderProfile = Depends(get_active_provider)):
    @sync_to_async
    def delete():
        count, _ = provider.availability_exceptions.filter(id=exception_id).delete()
        return count
    deleted = await delete()
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Exception not found")
    return {"message": "Exception deleted"}


@app.get("/api/provider/availability")
async def get_availability(provider: ProviderProfile = Depends(get_active_provider)):
    @sync_to_async
    def get():
        return list(provider.availabilities.values(
            "id", "day_of_week", "start_time", "end_time", "is_off", "max_bookings_per_day"
        ))
    availabilities = await get()
    return {"availability": availabilities}


@sync_to_async
def get_commission_percentage(service: Service) -> float:
    # Find active commission rule for the service's department
    rule = CommissionRule.objects.filter(
        department=service.category.department,
        is_active=True,
        effective_from__lte=datetime.now(),
        effective_to__isnull=True
    ).first()
    if not rule:
        rule = CommissionRule.objects.filter(
            department__isnull=True,
            is_active=True,
            effective_from__lte=datetime.now(),
            effective_to__isnull=True
        ).first()
    return rule.commission_percentage if rule else 0.0


@app.post("/api/provider/bookings/{booking_id}/complete")
async def complete_booking(
    booking_id: str,
    provider: ProviderProfile = Depends(get_active_provider)
):
    try:
        booking = await sync_to_async(Booking.objects.select_related('service').get)(
            id=booking_id, provider=provider
        )
    except Booking.DoesNotExist:
        raise HTTPException(status_code=404, detail="Booking not found for this provider")
    
    if booking.status != 'accepted':
        raise HTTPException(status_code=400, detail=f"Booking cannot be completed (current status: {booking.status})")
    
    # Calculate commission
    commission_pct = await get_commission_percentage(booking.service)
    commission_amount = (commission_pct / 100) * float(booking.total_amount)
    net_amount = float(booking.total_amount) - commission_amount
    
    @sync_to_async
    def update():
        booking.status = 'completed'
        booking.completed_at = datetime.now(timezone.utc)
        booking.commission_amount = commission_amount
        booking.save()
        
        # Create ProviderEarnings record
        ProviderEarnings.objects.create(
            booking=booking,
            provider=provider,
            total_amount=booking.total_amount,
            commission_amount=commission_amount,
            net_amount=net_amount,
            status='pending'
        )
        return True
    await update()
    client_email = booking.client.user.email
    await send_email_async(
        subject="Service Completed",
        message=f"Dear {booking.client.user.first_name},\n\nYour booking for '{booking.service.name}' has been marked as completed.\nWe hope you enjoyed the service. Please consider leaving a review.\n\nThank you.",
        recipient_list=[client_email]
    )
    return {
        "id": booking.id,
        "status": "completed",
        "total_amount": float(booking.total_amount),
        "commission_amount": commission_amount,
        "net_amount": net_amount,
        "message": "Booking completed and earnings recorded"
    }



@app.post("/api/bookings/{booking_id}/review")
async def create_review(
    booking_id: str,
    review_data: ReviewCreate,
    current_user: User = Depends(get_current_user)
):
    if current_user.role != 'client':
        raise HTTPException(status_code=403, detail="Only clients can write reviews")
    
    try:
        booking = await sync_to_async(Booking.objects.select_related('client', 'provider').get)(
            id=booking_id, client__user=current_user
        )
    except Booking.DoesNotExist:
        raise HTTPException(status_code=404, detail="Booking not found for this client")
    
    if booking.status != 'completed':
        raise HTTPException(status_code=400, detail="You can only review completed bookings")
    
    # Check if review already exists
    existing = await sync_to_async(Review.objects.filter(booking=booking).exists)()
    if existing:
        raise HTTPException(status_code=400, detail="You have already reviewed this booking")
    
    @sync_to_async
    def create():
        review = Review.objects.create(
            booking=booking,
            client=booking.client,
            provider=booking.provider,
            rating=review_data.rating,
            comment=review_data.comment,
            is_visible=True
        )
        # Update provider's average rating
        provider = booking.provider
        total_reviews = provider.total_reviews + 1
        new_avg = (provider.rating_avg * provider.total_reviews + review_data.rating) / total_reviews
        provider.rating_avg = round(new_avg, 2)
        provider.total_reviews = total_reviews
        provider.save()
        return review
    review = await create()
    return {
        "id": review.id,
        "rating": review.rating,
        "comment": review.comment,
        "message": "Review submitted"
    }



@app.get("/api/services/{service_id}/reviews")
async def get_service_reviews(service_id: str):
    @sync_to_async
    def get():
        return list(Review.objects.filter(
            booking__service__id=service_id,
            is_visible=True
        ).select_related('client__user', 'provider').values(
            "id", "rating", "comment", "created_at",
            "client__user__first_name", "client__user__last_name"
        ))
    reviews = await get()
    return {"count": len(reviews), "reviews": reviews}



@app.get("/api/admin/providers")
async def list_providers(
    status: Optional[str] = None,   # 'pending', 'approved', 'all'
    admin: User = Depends(require_role(["admin"]))
):
    @sync_to_async
    def get():
        qs = ProviderProfile.objects.select_related('user')
        if status == 'pending':
            qs = qs.filter(is_approved=False)
        elif status == 'approved':
            qs = qs.filter(is_approved=True)
        # else 'all' or None returns all
        return list(qs.values(
            "id", "business_name", "phone_number", "is_approved",
            "created_at", "user__email", "user__first_name", "user__last_name"
        ))
    providers = await get()
    return {"count": len(providers), "providers": providers}


@app.post("/api/admin/providers/{provider_id}/approval")
async def set_provider_approval(
    provider_id: str,
    action: ProviderApprovalAction,
    admin: User = Depends(require_role(["admin"]))
):
    try:
        provider = await sync_to_async(ProviderProfile.objects.select_related('user').get)(id=provider_id)
    except ProviderProfile.DoesNotExist:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    if action.approved == provider.is_approved:
        status_text = "approved" if action.approved else "rejected"
        raise HTTPException(status_code=400, detail=f"Provider is already {status_text}")
    
    @sync_to_async
    def update():
        provider.is_approved = action.approved
        if action.notes:
            # You could store notes in a separate field (e.g., admin_notes) – for now, optional
            pass
        provider.save()
        return provider
    await update()
    provider_email = provider.user.email
    if action.approved:
        await send_email_async(
            subject="Provider Profile Approved",
            message=f"Dear {provider.business_name},\n\nYour provider profile has been approved. You can now start creating services and accepting bookings.\n\nWelcome to Kyusa!",
            recipient_list=[provider_email]
        )  
    return {
        "id": provider.id,
        "business_name": provider.business_name,
        "is_approved": provider.is_approved,
        "message": f"Provider {'approved' if action.approved else 'rejected'}"
    }


@app.get("/api/provider/earnings/summary")
async def get_earnings_summary(provider: ProviderProfile = Depends(get_active_provider)):
    @sync_to_async
    def get_totals():
        total_pending = provider.earnings.filter(status='pending').aggregate(total=Sum('net_amount'))['total'] or 0
        total_available = provider.earnings.filter(status='available').aggregate(total=Sum('net_amount'))['total'] or 0
        total_paid = provider.earnings.filter(status='paid').aggregate(total=Sum('net_amount'))['total'] or 0
        return {
            "pending": float(total_pending),
            "available": float(total_available),
            "paid": float(total_paid),
            "total": float(total_pending + total_available + total_paid)
        }
    totals = await get_totals()
    return totals



@app.get("/api/provider/earnings")
async def list_earnings(
    status: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    provider: ProviderProfile = Depends(get_active_provider)
):
    @sync_to_async
    def get():
        qs = provider.earnings.select_related('booking').order_by('-booking__completed_at')
        if status:
            qs = qs.filter(status=status)
        total = qs.count()
        items = list(qs[offset:offset+limit].values(
            "id", "total_amount", "commission_amount", "net_amount", "status",
            "paid_at", "booking__id", "booking__service__name"
        ))
        return {"total": total, "earnings": items}
    return await get()



@app.post("/api/provider/payouts")
async def request_payout(
    payout_data: PayoutRequest,
    provider: ProviderProfile = Depends(get_active_provider)
):
    # Check if requested amount is available (sum of 'available' earnings)
    @sync_to_async
    def get_available():
        total = provider.earnings.filter(status='available').aggregate(total=Sum('net_amount'))['total'] or 0
        return float(total)
    available = await get_available()
    if payout_data.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    if payout_data.amount > available:
        raise HTTPException(status_code=400, detail=f"Insufficient available balance. Maximum available: {available}")
    
    @sync_to_async
    def create_payout():
        # Create payout record
        payout = Payout.objects.create(
            provider=provider,
            amount=payout_data.amount,
            status='requested',
            destination=payout_data.destination,
            notes=payout_data.notes,
            requested_at=datetime.now(timezone.utc)
        )
        # Mark corresponding earnings as 'paid'? Usually you'd link earnings to payout.
        # For simplicity, we'll update earnings status later when payout is processed.
        # Here we just create the payout.
        return payout
    payout = await create_payout()
    return {"id": payout.id, "amount": payout.amount, "status": payout.status, "message": "Payout requested"}


@app.post("/api/admin/earnings/{earning_id}/release")
async def release_earning(earning_id: str, admin: User = Depends(require_role(["admin"]))):
    try:
        earning = await sync_to_async(ProviderEarnings.objects.get)(id=earning_id, status='pending')
    except ProviderEarnings.DoesNotExist:
        raise HTTPException(status_code=404, detail="Earning not found or already released")
    @sync_to_async
    def update():
        earning.status = 'available'
        earning.save()
    await update()
    return {"id": earning.id, "status": "available", "message": "Earning released for payout"}


# favorites

@app.post("/api/favorites/{service_id}")
async def add_favorite(service_id: str, current_user: User = Depends(get_current_user)):
    if current_user.role != 'client':
        raise HTTPException(status_code=403, detail="Only clients can add favorites")
    
    try:
        client = await sync_to_async(ClientProfile.objects.get)(user=current_user)
    except ClientProfile.DoesNotExist:
        raise HTTPException(status_code=400, detail="Client profile not found")
    
    try:
        service = await sync_to_async(Service.objects.get)(id=service_id, is_active=True)
    except Service.DoesNotExist:
        raise HTTPException(status_code=404, detail="Service not found")
    
    # Check if already favorited
    exists = await sync_to_async(Favorite.objects.filter(client=client, service=service).exists)()
    if exists:
        raise HTTPException(status_code=400, detail="Service already in favorites")
    
    @sync_to_async
    def create():
        return Favorite.objects.create(client=client, service=service)
    fav = await create()
    return {"id": fav.id, "message": "Service added to favorites"}


@app.delete("/api/favorites/{service_id}")
async def remove_favorite(service_id: str, current_user: User = Depends(get_current_user)):
    if current_user.role != 'client':
        raise HTTPException(status_code=403, detail="Only clients can remove favorites")
    
    try:
        client = await sync_to_async(ClientProfile.objects.get)(user=current_user)
    except ClientProfile.DoesNotExist:
        raise HTTPException(status_code=400, detail="Client profile not found")
    
    try:
        service = await sync_to_async(Service.objects.get)(id=service_id)
    except Service.DoesNotExist:
        raise HTTPException(status_code=404, detail="Service not found")
    
    deleted = await sync_to_async(Favorite.objects.filter(client=client, service=service).delete)()
    if deleted[0] == 0:
        raise HTTPException(status_code=404, detail="Favorite not found")
    return {"message": "Service removed from favorites"}


@app.get("/api/favorites")
async def list_favorites(current_user: User = Depends(get_current_user)):
    if current_user.role != 'client':
        raise HTTPException(status_code=403, detail="Only clients can view favorites")
    
    try:
        client = await sync_to_async(ClientProfile.objects.get)(user=current_user)
    except ClientProfile.DoesNotExist:
        raise HTTPException(status_code=400, detail="Client profile not found")
    
    @sync_to_async
    def get():
        return list(client.favorites.select_related('service').values(
            "id", "service__id", "service__name", "service__base_price", "created_at"
        ))
    favorites = await get()
    # Convert to list of dicts with proper keys
    results = [
        {
            "id": fav["id"],
            "service_id": fav["service__id"],
            "service_name": fav["service__name"],
            "service_base_price": fav["service__base_price"],
            "created_at": fav["created_at"],
        }
        for fav in favorites
    ]
    return {"count": len(results), "favorites": results}




@app.get("/api/provider/analytics/dashboard")
async def provider_analytics(provider: ProviderProfile = Depends(get_active_provider)):
    @sync_to_async
    def get_stats():
        # Booking counts by status
        booking_counts = Booking.objects.filter(provider=provider).values('status').annotate(count=Count('id'))
        total_bookings = Booking.objects.filter(provider=provider).count()
        
        # Completed bookings total amount
        completed_total = Booking.objects.filter(provider=provider, status='completed').aggregate(total=Sum('total_amount'))['total'] or 0
        
        # Earnings summary
        earnings_summary = provider.earnings.aggregate(
            total_pending=Sum('net_amount', filter=Q(status='pending')),
            total_available=Sum('net_amount', filter=Q(status='available')),
            total_paid=Sum('net_amount', filter=Q(status='paid')),
        )
        
        # Monthly bookings (last 6 months)
        
        monthly_bookings = Booking.objects.filter(provider=provider, status='completed').annotate(month=TruncMonth('completed_at')).values('month').annotate(count=Count('id'), revenue=Sum('total_amount')).order_by('-month')[:6]
        
        return {
            "booking_counts": list(booking_counts),
            "total_bookings": total_bookings,
            "completed_revenue": float(completed_total),
            "earnings": {
                "pending": float(earnings_summary['total_pending'] or 0),
                "available": float(earnings_summary['total_available'] or 0),
                "paid": float(earnings_summary['total_paid'] or 0),
            },
            "monthly_breakdown": [
                {
                    "month": item['month'].strftime("%Y-%m"),
                    "bookings": item['count'],
                    "revenue": float(item['revenue'])
                } for item in monthly_bookings
            ]
        }
    return await get_stats()


@sync_to_async
def send_email_async(subject, message, recipient_list):
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False,
        )
    except Exception as e:
        print(f"Email failed: {e}")



@sync_to_async
def get_setting(key: str, default=None):
    try:
        setting = SystemSetting.objects.get(key=key)
        if setting.value_type == 'int':
            return int(setting.value)
        elif setting.value_type == 'bool':
            return setting.value.lower() in ('true', '1', 'yes')
        elif setting.value_type == 'json':
            import json
            return json.loads(setting.value)
        return setting.value
    except SystemSetting.DoesNotExist:
        return default

@sync_to_async
def set_setting(key: str, value, value_type='string', description='', is_public=False):
    # Convert value to string based on type
    if value_type == 'int':
        str_value = str(int(value))
    elif value_type == 'bool':
        str_value = 'true' if value else 'false'
    elif value_type == 'json':
        import json
        str_value = json.dumps(value)
    else:
        str_value = str(value)
    
    obj, created = SystemSetting.objects.update_or_create(
        key=key,
        defaults={
            'value': str_value,
            'value_type': value_type,
            'description': description,
            'is_public': is_public,
        }
    )
    return obj



@app.get("/api/settings/public")
async def get_public_settings():
    @sync_to_async
    def get():
        qs = SystemSetting.objects.filter(is_public=True)
        result = {}
        for setting in qs:
            if setting.value_type == 'int':
                result[setting.key] = int(setting.value)
            elif setting.value_type == 'bool':
                result[setting.key] = setting.value.lower() in ('true', '1', 'yes')
            elif setting.value_type == 'json':
                import json
                result[setting.key] = json.loads(setting.value)
            else:
                result[setting.key] = setting.value
        return result
    return await get()




@app.get("/api/admin/settings")
async def list_settings(admin: User = Depends(require_role(["admin"]))):
    @sync_to_async
    def get():
        return list(SystemSetting.objects.values())
    return await get()

@app.post("/api/admin/settings/{key}")
async def update_setting(key: str, data: SettingUpdate, admin: User = Depends(require_role(["admin"]))):
    try:
        await set_setting(
            key=key,
            value=data.value,
            value_type=data.value_type,
            description=data.description,
            is_public=data.is_public
        )
        return {"key": key, "message": "Setting updated"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/disputes")
async def create_dispute(
    dispute_data: DisputeCreate,
    current_user: User = Depends(get_current_user)
):
    if current_user.role != 'client':
        raise HTTPException(status_code=403, detail="Only clients can open disputes")
    
    try:
        booking = await sync_to_async(Booking.objects.select_related('client', 'provider').get)(
            id=dispute_data.booking_id,
            client__user=current_user
        )
    except Booking.DoesNotExist:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Check if dispute already exists for this booking
    existing = await sync_to_async(Dispute.objects.filter(booking=booking).exists)()
    if existing:
        raise HTTPException(status_code=400, detail="A dispute already exists for this booking")
    
    @sync_to_async
    def create():
        return Dispute.objects.create(
            booking=booking,
            raised_by=current_user,
            reason=dispute_data.reason,
            status='open'
        )
    dispute = await create()
    return {
        "id": dispute.id,
        "booking_id": dispute.booking.id,
        "status": dispute.status,
        "message": "Dispute opened. Admin will review shortly."
    }



    

@app.post("/api/disputes/{dispute_id}/evidence")
async def upload_evidence(
    dispute_id: str,
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user)
):
    # Fetch dispute with related objects in a sync_to_async block
    @sync_to_async
    def get_dispute_and_users():
        try:
            dispute = Dispute.objects.select_related('booking__provider__user', 'raised_by').get(id=dispute_id)
            # Extract IDs for async permission check
            raised_by_id = dispute.raised_by.id
            provider_user_id = dispute.booking.provider.user.id
            return dispute, raised_by_id, provider_user_id
        except Dispute.DoesNotExist:
            return None, None, None
    
    dispute, raised_by_id, provider_user_id = await get_dispute_and_users()
    if not dispute:
        raise HTTPException(status_code=404, detail="Dispute not found")
    
    # Async permission check (using IDs)
    if current_user.id not in [raised_by_id, provider_user_id] and current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Not authorized to upload evidence for this dispute")
    
    # Save file
    import os
    from django.core.files.base import ContentFile
    file_content = await file.read()
    safe_filename = file.filename.replace(' ', '_')
    file_name = f"dispute_{dispute_id}_{int(datetime.now().timestamp())}_{safe_filename}"
    
    @sync_to_async
    def save_evidence():
        evidence = DisputeEvidence.objects.create(
            dispute=dispute,
            uploaded_by=current_user,
            description=description,
        )
        evidence.file.save(file_name, ContentFile(file_content))
        return evidence
    
    evidence = await save_evidence()
    return {"id": evidence.id, "message": "Evidence uploaded"}


@app.get("/api/disputes")
async def list_disputes(
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    # Admin sees all; provider sees disputes related to their bookings; client sees their own
    @sync_to_async
    def get():
        if current_user.role == 'admin':
            qs = Dispute.objects.all()
        elif current_user.role == 'provider':
            qs = Dispute.objects.filter(booking__provider__user=current_user)
        else:
            qs = Dispute.objects.filter(raised_by=current_user)
        
        if status:
            qs = qs.filter(status=status)
        return list(qs.values("id", "booking_id", "reason", "status", "created_at", "resolution_notes"))
    disputes = await get()
    return {"count": len(disputes), "disputes": disputes}



@app.get("/api/disputes/{dispute_id}/evidence")
async def get_evidence(
    dispute_id: str,
    current_user: User = Depends(get_current_user)
):
    @sync_to_async
    def get_dispute_and_evidence():
        try:
            dispute = Dispute.objects.select_related('raised_by', 'booking__provider__user').get(id=dispute_id)
            # Extract IDs for permission check
            raised_by_id = dispute.raised_by.id
            provider_user_id = dispute.booking.provider.user.id
            # Get evidence list (values)
            evidence_list = list(dispute.evidences.values("id", "description", "file", "uploaded_at", "uploaded_by__email"))
            return dispute, raised_by_id, provider_user_id, evidence_list
        except Dispute.DoesNotExist:
            return None, None, None, None
    
    dispute, raised_by_id, provider_user_id, evidence_list = await get_dispute_and_evidence()
    if not dispute:
        raise HTTPException(status_code=404, detail="Dispute not found")
    
    # Permission check
    if current_user.role != 'admin' and current_user.id not in [raised_by_id, provider_user_id]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return {"evidence": evidence_list}




class DisputeResolve(BaseModel):
    status: str   # 'resolved_closed' or 'resolved_refund'
    resolution_notes: Optional[str] = None

@app.post("/api/admin/disputes/{dispute_id}/resolve")
async def resolve_dispute(
    dispute_id: str,
    data: DisputeResolve,
    admin: User = Depends(require_role(["admin"]))
):
    try:
        dispute = await sync_to_async(Dispute.objects.select_related('booking').get)(id=dispute_id)
    except Dispute.DoesNotExist:
        raise HTTPException(status_code=404, detail="Dispute not found")
    
    if dispute.status not in ['open', 'under_review']:
        raise HTTPException(status_code=400, detail="Dispute already resolved")
    
    @sync_to_async
    def update():
        dispute.status = data.status
        dispute.resolution_notes = data.resolution_notes
        dispute.resolved_by = admin
        dispute.resolved_at = datetime.now(timezone.utc)
        dispute.save()
        return dispute
    dispute = await update()
    return {
        "id": dispute.id,
        "status": dispute.status,
        "message": f"Dispute resolved as {data.status}"
    }

