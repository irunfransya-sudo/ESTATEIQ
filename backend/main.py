from datetime import datetime, timedelta
from typing import Optional, List

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text, func, text
from sqlalchemy.orm import sessionmaker, declarative_base, Session, relationship

DATABASE_URL = "sqlite:///./realestate.db"
SECRET_KEY = "real-estate-insight-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 24 * 60

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

app = FastAPI(title="RealEstate Insight API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="buyer")

    requests = relationship("Request", back_populates="user")


class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    property_type = Column(String, nullable=False)
    district = Column(String, nullable=False)
    address = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    area = Column(Float, nullable=False)
    rooms = Column(Integer, default=1)
    floor = Column(Integer, default=1)
    total_floors = Column(Integer, default=1)
    year_built = Column(Integer, default=2010)
    condition = Column(String, default="житловий стан")
    infrastructure_score = Column(Integer, default=7)
    demand_score = Column(Integer, default=7)
    latitude = Column(Float, default=50.4501)
    longitude = Column(Float, default=30.5234)
    image_url = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Request(Base):
    __tablename__ = "requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    property_id = Column(Integer, ForeignKey("properties.id"))

    comment = Column(Text, nullable=True)
    phone = Column(String, nullable=True)

    status = Column(String, default="нова")
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="requests")
    property = relationship("Property")


class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: str = "buyer"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    full_name: str
    email: str
    role: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserOut


class PropertyBase(BaseModel):
    title: str
    property_type: str
    district: str
    address: str
    price: float
    area: float
    rooms: int = 1
    floor: int = 1
    total_floors: int = 1
    year_built: int = 2010
    condition: str = "житловий стан"
    infrastructure_score: int = 7
    demand_score: int = 7
    latitude: float = 50.4501
    longitude: float = 30.5234
    image_url: Optional[str] = None
    description: Optional[str] = None


class PropertyCreate(PropertyBase):
    pass


class PropertyOut(PropertyBase):
    id: int
    price_per_m2: float
    smart_score: float
    investment_index: float
    predicted_price: float

    class Config:
        from_attributes = True


class RequestCreate(BaseModel):
    property_id: int
    comment: Optional[str] = None
    phone: Optional[str] = None


class RequestOut(BaseModel):
    id: int
    status: str
    comment: Optional[str]
    phone: Optional[str]
    created_at: datetime
    property: PropertyOut
    user: UserOut

    class Config:
        from_attributes = True


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")

        if email is None:
            raise HTTPException(status_code=401, detail="Не вдалося перевірити користувача")

    except JWTError:
        raise HTTPException(status_code=401, detail="Недійсний токен")

    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=401, detail="Користувача не знайдено")

    return user


def require_manager(user: User = Depends(get_current_user)):
    if user.role not in ["manager", "analyst", "admin"]:
        raise HTTPException(status_code=403, detail="Доступ лише для аналітика/менеджера")

    return user


def property_metrics(p: Property):
    price_per_m2 = round(p.price / p.area, 2) if p.area else 0

    condition_map = {
        "без ремонту": 3,
        "житловий стан": 6,
        "після ремонту": 8,
        "новобудова": 9,
        "преміум": 10,
    }

    condition_score = condition_map.get(p.condition.lower(), 6)

    smart_score = round(
        (p.infrastructure_score * 0.35 + p.demand_score * 0.35 + condition_score * 0.3) * 10,
        1,
    )

    investment_index = round(
        (p.demand_score * 0.4 + p.infrastructure_score * 0.35 + condition_score * 0.25) * 10,
        1,
    )

    predicted_price = round(p.price * 1.05, 0)

    return price_per_m2, smart_score, investment_index, predicted_price


def to_property_out(p: Property, db: Session):
    price_per_m2, smart_score, investment_index, predicted_price = property_metrics(p)

    data = {
        c.name: getattr(p, c.name)
        for c in Property.__table__.columns
        if c.name != "created_at"
    }

    data.update({
        "price_per_m2": price_per_m2,
        "smart_score": smart_score,
        "investment_index": investment_index,
        "predicted_price": predicted_price,
    })

    return PropertyOut(**data)


def to_request_out(req: Request, db: Session):
    return RequestOut(
        id=req.id,
        status=req.status,
        comment=req.comment,
        phone=req.phone,
        created_at=req.created_at,
        property=to_property_out(req.property, db),
        user=req.user,
    )


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

    with engine.connect() as conn:
        columns = conn.execute(text("PRAGMA table_info(requests)")).fetchall()
        column_names = [column[1] for column in columns]

        if "phone" not in column_names:
            conn.execute(text("ALTER TABLE requests ADD COLUMN phone VARCHAR"))
            conn.commit()

    db = SessionLocal()

    if db.query(User).count() == 0:
        db.add_all([
            User(
                full_name="Аналітик",
                email="analyst@example.com",
                hashed_password=get_password_hash("analyst123"),
                role="analyst",
            ),
            User(
                full_name="Покупець",
                email="buyer@example.com",
                hashed_password=get_password_hash("buyer123"),
                role="buyer",
            ),
        ])

    if db.query(Property).count() == 0:
        db.add_all([
            Property(
                title="2-кімнатна квартира біля метро",
                property_type="квартира",
                district="Печерський",
                address="вул. Коновальця, 32",
                price=135000,
                area=62,
                rooms=2,
                floor=8,
                total_floors=16,
                year_built=2018,
                condition="після ремонту",
                infrastructure_score=9,
                demand_score=9,
                image_url="https://images.unsplash.com/photo-1560448204-e02f11c3d0e2",
                description="Сучасна квартира з хорошою транспортною доступністю.",
            ),
            Property(
                title="Смарт-квартира у новобудові",
                property_type="квартира",
                district="Солом'янський",
                address="просп. Повітрофлотський, 56",
                price=59000,
                area=32,
                rooms=1,
                floor=12,
                total_floors=25,
                year_built=2022,
                condition="новобудова",
                infrastructure_score=8,
                demand_score=8,
                image_url="https://images.unsplash.com/photo-1522708323590-d24dbb6b0267",
                description="Компактне житло для оренди або інвестування.",
            ),
            Property(
                title="Будинок у передмісті",
                property_type="будинок",
                district="Бучанський",
                address="м. Ірпінь, вул. Центральна",
                price=185000,
                area=145,
                rooms=5,
                floor=1,
                total_floors=2,
                year_built=2020,
                condition="після ремонту",
                infrastructure_score=7,
                demand_score=8,
                image_url="https://images.unsplash.com/photo-1564013799919-ab600027ffc6",
                description="Приватний будинок з ділянкою та паркомісцем.",
            ),
            Property(
                title="Комерційне приміщення",
                property_type="комерційна",
                district="Шевченківський",
                address="вул. Січових Стрільців, 18",
                price=220000,
                area=86,
                rooms=3,
                floor=1,
                total_floors=6,
                year_built=2015,
                condition="преміум",
                infrastructure_score=9,
                demand_score=7,
                image_url="https://images.unsplash.com/photo-1497366754035-f200968a6e72",
                description="Об’єкт для бізнесу у центральній частині міста.",
            ),
            Property(
                title="1-кімнатна квартира на Позняках",
                property_type="квартира",
                district="Дарницький",
                address="просп. Григоренка, 24",
                price=72000,
                area=43,
                rooms=1,
                floor=10,
                total_floors=22,
                year_built=2016,
                condition="житловий стан",
                infrastructure_score=8,
                demand_score=8,
                image_url="https://images.unsplash.com/photo-1502672260266-1c1ef2d93688",
                description="Ліквідний об’єкт для проживання або орендного бізнесу.",
            ),
        ])

    db.commit()
    db.close()


@app.get("/")
def root():
    return {"message": "RealEstate Insight API працює"}


@app.post("/auth/register", response_model=Token)
def register(data: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email вже зареєстрований")

    user = User(
        full_name=data.full_name,
        email=data.email,
        hashed_password=get_password_hash(data.password),
        role=data.role,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": user.email})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user,
    }


@app.post("/auth/login", response_model=Token)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Неправильний email або пароль")

    token = create_access_token({"sub": user.email})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user,
    }


@app.get("/properties/", response_model=List[PropertyOut])
def get_properties(
    type: Optional[str] = None,
    district: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    rooms: Optional[int] = None,
    db: Session = Depends(get_db),
):
    q = db.query(Property)

    if type:
        q = q.filter(Property.property_type == type)

    if district:
        q = q.filter(Property.district.ilike(f"%{district}%"))

    if min_price is not None:
        q = q.filter(Property.price >= min_price)

    if max_price is not None:
        q = q.filter(Property.price <= max_price)

    if rooms is not None:
        q = q.filter(Property.rooms == rooms)

    properties = q.order_by(Property.id.desc()).all()

    return [to_property_out(p, db) for p in properties]


@app.get("/properties/{property_id}", response_model=PropertyOut)
def get_property(property_id: int, db: Session = Depends(get_db)):
    p = db.query(Property).filter(Property.id == property_id).first()

    if not p:
        raise HTTPException(status_code=404, detail="Об’єкт не знайдено")

    return to_property_out(p, db)


@app.post("/properties/", response_model=PropertyOut)
def create_property(
    data: PropertyCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_manager),
):
    p = Property(**data.dict())

    db.add(p)
    db.commit()
    db.refresh(p)

    return to_property_out(p, db)


@app.delete("/properties/{property_id}")
def delete_property(
    property_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_manager),
):
    p = db.query(Property).filter(Property.id == property_id).first()

    if not p:
        raise HTTPException(status_code=404, detail="Об’єкт не знайдено")

    db.delete(p)
    db.commit()

    return {"message": "Об’єкт видалено"}


@app.post("/requests/", response_model=RequestOut)
def create_request(
    data: RequestCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    p = db.query(Property).filter(Property.id == data.property_id).first()

    if not p:
        raise HTTPException(status_code=404, detail="Об’єкт не знайдено")

    req = Request(
        user_id=user.id,
        property_id=p.id,
        comment=data.comment,
        phone=data.phone,
    )

    db.add(req)
    db.commit()
    db.refresh(req)

    return to_request_out(req, db)


@app.get("/requests/", response_model=List[RequestOut])
def get_requests(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if user.role in ["manager", "analyst", "admin"]:
        requests = db.query(Request).order_by(Request.id.desc()).all()
    else:
        requests = (
            db.query(Request)
            .filter(Request.user_id == user.id)
            .order_by(Request.id.desc())
            .all()
        )

    return [to_request_out(req, db) for req in requests]


@app.delete("/requests/{request_id}")
def delete_request(
    request_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    req = db.query(Request).filter(Request.id == request_id).first()

    if not req:
        raise HTTPException(status_code=404, detail="Заявку не знайдено")

    if user.role == "buyer" and req.user_id != user.id:
        raise HTTPException(status_code=403, detail="Можна видаляти лише власні заявки")

    db.delete(req)
    db.commit()

    return {"message": "Заявку видалено"}


@app.get("/analytics/summary")
def summary(db: Session = Depends(get_db)):
    properties = db.query(Property).all()

    total = len(properties)
    avg_price = db.query(func.avg(Property.price)).scalar() or 0
    avg_m2 = db.query(func.avg(Property.price / Property.area)).scalar() or 0

    districts = (
        db.query(
            Property.district,
            func.count(Property.id),
            func.avg(Property.price / Property.area),
        )
        .group_by(Property.district)
        .all()
    )

    types = (
        db.query(
            Property.property_type,
            func.count(Property.id),
            func.avg(Property.price),
        )
        .group_by(Property.property_type)
        .all()
    )

    top = []

    for p in properties:
        out = to_property_out(p, db)
        top.append({
            "id": p.id,
            "title": p.title,
            "district": p.district,
            "score": out.smart_score,
            "investment_index": out.investment_index,
        })

    top = sorted(top, key=lambda x: x["investment_index"], reverse=True)[:5]

    return {
        "total_properties": total,
        "average_price": round(avg_price, 2),
        "average_price_per_m2": round(avg_m2, 2),
        "districts": [
            {
                "district": d,
                "count": c,
                "avg_price_per_m2": round(a or 0, 2),
            }
            for d, c, a in districts
        ],
        "types": [
            {
                "type": t,
                "count": c,
                "avg_price": round(a or 0, 2),
            }
            for t, c, a in types
        ],
        "top_investment": top,
    }