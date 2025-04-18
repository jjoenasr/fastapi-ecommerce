from database import User, Product, create_tables, get_session
from utils import hash_password
from faker import Faker

faker = Faker()
Faker.seed(4321) # Seed for reproducibility

def create_fake_product() -> Product:
    return Product(
        name=faker.catch_phrase(),
        price=round(faker.pyfloat(left_digits=2, right_digits=2, positive=True), 2),
        description=faker.sentence()
    )

def create_fake_users() -> list[User]:
    return [
        User(
            username=faker.user_name(),
            email='admin@gmail.com',
            password_hash=hash_password('admin'),  # Use a default password for seeding
        ),
        User(
            username=faker.user_name(),
            email='guest@gmail.com',
            password_hash=hash_password('guest'), # Use a default password for seeding
        )
    ]

def populate_db():
    create_tables()  # Create tables
    session_gen = get_session()
    db = next(session_gen)  # Get a session from the generator
    try:
        # Generate 20 fake products
        fake_products = [create_fake_product() for _ in range(20)]
        db.add_all(fake_products)  # Add all products to the session
        fake_users = create_fake_users()  # Generate fake users
        db.add_all(fake_users)  # Add all users to the session
        db.commit()  # Commit to the database
        print("Database populated with fake products.")
    finally:
        db.close()

if __name__ == "__main__":
    populate_db()