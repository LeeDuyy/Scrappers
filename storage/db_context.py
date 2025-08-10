from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from model.post import Base

# Tạo thư mục lưu DB
os.makedirs("storage", exist_ok=True)

# Đường dẫn tới file DB
db_path = os.path.join("storage", "scrapper.db")

engine = create_engine(
    f"sqlite:///{db_path}",
    echo=False,
    connect_args={"timeout": 15, "check_same_thread": False}
)

# Tạo bảng nếu chưa có
Base.metadata.create_all(engine)

# Tạo Session factory — KHÔNG tạo session global ở đây
# expire_on_commit=False giúp object vẫn giữ giá trị sau commit nếu cần dùng
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)