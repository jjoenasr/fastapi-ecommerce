from database import User, Product, create_tables, get_session
from supabase_client import get_supabase
import uuid
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
    sp = get_supabase()
    # Create a list of users with their email and password
    sp_users = [
        {
            "email": 'admin@gmail.com',
            "password": 'admin123',
        },
        {
            "email": 'guest@gmail.com',
            "password": 'guest123',
        }
    ]
    # Create a new user in Supabase for each user in the list
    for user in sp_users:
        # Create a new user in Supabase
        response = sp.auth.sign_up(
            {
            "email" : user["email"],
            "password": user["password"]
            }
        )
        if not response or not response.user:
            raise Exception("Supabase sign-up failed")
        user['id'] = uuid.UUID(response.user.id)
        
    users = [
        User(
            id=sp_users[0]["id"],
            username=faker.user_name(),
            email=sp_users[0]["email"],
            first_name=faker.first_name(),
            last_name=faker.last_name()
        ),
        User(
            id=sp_users[1]["id"],
            username=faker.user_name(),
            email=sp_users[1]["email"],
            first_name=faker.first_name(),
            last_name=faker.last_name()
        )
    ]
    return users


def populate_db():
    create_tables()  # Create tables
    session_gen = get_session()
    db = next(session_gen)  # Get a session from the generator
    try:
        # Generate 20 fake products
        fake_products = [create_fake_product() for _ in range(20)]
        db.add_all(fake_products)  # Add all products to the session
        fake_users = create_fake_users()
        db.add_all(fake_users)  # Add all users to the session
        db.commit()  # Commit to the database
        print("Database populated with fake products.")
    finally:
        db.close()

if __name__ == "__main__":
    populate_db()