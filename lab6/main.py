from fastapi import FastAPI, Depends
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pymongo import MongoClient
import redis
import kafka
import json
import time

# Инициализация FastAPI
app = FastAPI()

# === PostgreSQL ===
DATABASE_URL = "postgresql://myuser:mypassword@postgres:5432/mydatabase"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users/")
def create_user(username: str, email: str, db: SessionLocal = Depends(get_db)):
    user = User(username=username, email=email)
    db.add(user)
    db.commit()
    db.refresh(user)
    producer.send("user-events", {"event": "user_created", "username": username})
    return user

@app.get("/users/")
def get_users(db: SessionLocal = Depends(get_db)):
    return db.query(User).all()

# === MongoDB ===
MONGO_URI = "mongodb://mongo:27017"
mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client["mydatabase"]

@app.post("/mongo/")
def create_mongo_data(data: dict):
    mongo_db["data"].insert_one(data)
    return {"status": "Data added to MongoDB"}

@app.get("/mongo/")
def get_mongo_data():
    return list(mongo_db["data"].find())

# === Redis ===
redis_client = redis.StrictRedis(host="redis", port=6379, db=0)

@app.post("/cache/")
def cache_data(key: str, value: str):
    redis_client.set(key, value)
    return {"status": "Data cached"}

@app.get("/cache/")
def get_cached_data(key: str):
    value = redis_client.get(key)
    return {"value": value.decode("utf-8") if value else None}

# === Kafka ===
KAFKA_BROKER = "kafka:9092"

def wait_for_kafka():
    for _ in range(5):
        try:
            producer = kafka.KafkaProducer(
                bootstrap_servers=KAFKA_BROKER,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            )
            return producer
        except kafka.errors.NoBrokersAvailable:
            print("Kafka not available, retrying...")
            time.sleep(5)
    raise Exception("Kafka is not available after multiple retries")

producer = wait_for_kafka()

@app.post("/kafka/")
def send_kafka_message(topic: str, message: dict):
    producer.send(topic, message)
    producer.flush()
    return {"status": "Message sent"}
