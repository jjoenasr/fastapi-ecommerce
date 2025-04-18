from database import UserDocument, ProductDocument, OrderDocument, init_db
from utils import hash_password
from faker import Faker
import asyncio

faker = Faker()
Faker.seed(4321) # Seed for reproducibility

def create_fake_product() -> ProductDocument:
    return ProductDocument(
        name=faker.catch_phrase(),
        price=round(faker.pyfloat(left_digits=2, right_digits=2, positive=True), 2),
        description=faker.sentence()
    )

def create_fake_users() -> list[UserDocument]:
    return [
        UserDocument(
            username=faker.user_name(),
            email='admin@gmail.com',
            password_hash=hash_password('admin'),
        ),
        UserDocument(
            username=faker.user_name(),
            email='guest@gmail.com',
            password_hash=hash_password('guest'),
        )
    ]


# ✅ Seed function
async def populate_db():
    await init_db()

    # Remove existing data (optional for clean seeding)
    await UserDocument.delete_all()
    await ProductDocument.delete_all()
    await OrderDocument.delete_all()

    fake_products = [create_fake_product() for _ in range(20)]
    fake_users = create_fake_users()

    # Bulk insert
    await ProductDocument.insert_many(fake_products)
    await UserDocument.insert_many(fake_users)

    print("MongoDB populated with fake products and users.")


# ✅ Entry point
if __name__ == "__main__":
    asyncio.run(populate_db())