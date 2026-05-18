"""
建立第一個管理員帳號
用法：python scripts/create_admin.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv()

from app import create_app
from app.extensions import db
from app.models.user import User, UserRole


def main():
    app = create_app("development")
    with app.app_context():
        db.create_all()

        print("=== 建立管理員帳號 ===")
        email    = input("Email: ").strip()
        username = input("Username: ").strip()
        password = input("Password (min 8 chars): ").strip()

        if len(password) < 8:
            print("密碼至少需要 8 個字元。")
            return

        if User.query.filter_by(email=email).first():
            print(f"帳號 {email} 已存在。")
            return

        user = User(email=email, username=username, role=UserRole.admin)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        print(f"\n✓ 管理員帳號建立成功：{username} ({email})")
        print("  登入網址：http://localhost:5000/admin/login")


if __name__ == "__main__":
    main()
