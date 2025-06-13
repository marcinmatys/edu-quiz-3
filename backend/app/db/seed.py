import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Level, User

async def seed_levels(db: AsyncSession):
    """Seed predefined difficulty levels into the database"""
    # Only seed if the table is empty
    result = await db.execute(select(Level))
    if result.scalars().first() is None:
        print("Seeding levels...")
        levels_data = [
            {"code": "I", "description": "Klasa I", "level": 1},
            {"code": "II", "description": "Klasa II", "level": 2},
            {"code": "III", "description": "Klasa III", "level": 3},
            {"code": "IV", "description": "Klasa IV", "level": 4},
            {"code": "V", "description": "Klasa V", "level": 5},
            {"code": "VI", "description": "Klasa VI", "level": 6},
            {"code": "VII", "description": "Klasa VII", "level": 7},
            {"code": "VIII", "description": "Klasa VIII", "level": 8},
        ]
        for level_data in levels_data:
            level = Level(**level_data)
            db.add(level)
        await db.commit()
        print(f"Seeded {len(levels_data)} levels.")

async def seed_default_users(db: AsyncSession):
    """Seed default admin and student users"""
    result = await db.execute(select(User))
    if result.scalars().first() is None:
        print("Seeding default users...")
        # Create a default admin user
        admin_password = "admin123"  # In production, use a secure password
        admin_hashed_pw = bcrypt.hashpw(admin_password.encode(), bcrypt.gensalt()).decode()
        admin = User(
            username="admin",
            hashed_password=admin_hashed_pw,
            role="admin"
        )
        # Create a default student user
        student_password = "student123"  # In production, use a secure password
        student_hashed_pw = bcrypt.hashpw(student_password.encode(), bcrypt.gensalt()).decode()
        student = User(
            username="student",
            hashed_password=student_hashed_pw,
            role="student"
        )
        db.add(admin)
        db.add(student)
        await db.commit()
        print("Seeded default admin and student users.")

async def seed_database(db: AsyncSession):
    """Run all seed functions"""
    await seed_levels(db)
    await seed_default_users(db)
    print("Database seeding completed successfully.") 