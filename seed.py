from datetime import datetime, timezone, timedelta
import random

from sqlmodel import Session, select

from database import engine
from models import Campaign


def seed_database():

    with Session(engine) as session:

        existing = session.exec(select(Campaign)).first()

        if existing:
            print("Database already seeded.")
            return

        campaign_names = [
            "Summer Launch",
            "Black Friday",
            "Winter Sale",
            "Spring Promo",
            "Cyber Monday",
            "Holiday Blast",
            "Rainy Season Offer",
            "Diwali Deals",
            "New Year Campaign",
            "Flash Sale"
        ]

        campaigns = []

        for i in range(70):

            campaign = Campaign(
                name=f"{random.choice(campaign_names)} #{i + 1}",
                due_date=datetime.now(timezone.utc)
                + timedelta(days=random.randint(1, 365))
            )

            campaigns.append(campaign)

        session.add_all(campaigns)
        session.commit()

        print("70 campaigns inserted successfully.")