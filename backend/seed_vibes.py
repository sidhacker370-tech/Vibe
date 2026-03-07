import asyncio
import uuid
import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.models.vibe import Vibe, VibeMember
from app.core.security import hash_password

async def seed_starter_vibes():
    async with AsyncSessionLocal() as db:
        print("Checking for existing Admin user...")
        # Get or create admin user
        admin_result = await db.execute(select(User).where(User.username == "VibeOfficial"))
        admin_user = admin_result.scalars().first()
        
        if not admin_user:
            print("Creating VibeOfficial user...")
            hashed_pwd = hash_password("SecureVibe2026!")
            admin_user = User(
                id=str(uuid.uuid4()),
                username="VibeOfficial",
                email="hello@vibe.com",
                hashed_password=hashed_pwd,
                influence_score=9999
            )
            db.add(admin_user)
            await db.commit()
            await db.refresh(admin_user)
            
        starter_vibes = [
            {"name": "Startup Builders", "description": "Share your MRR, roast landings, build in public."},
            {"name": "College Coders", "description": "Hackathons, leetcode, and surviving CS degrees."},
            {"name": "Late Night Programmers", "description": "Dark mode enthusiasts coding till 4 AM."},
            {"name": "Gym Motivation", "description": "PRs, gym routines, and nutrition talk."},
            {"name": "Anime Lounge", "description": "Seasonal anime discussions, manga recommendations."}
        ]
        
        for vibe_data in starter_vibes:
            vibe_result = await db.execute(select(Vibe).where(Vibe.name == vibe_data["name"]))
            existing_vibe = vibe_result.scalars().first()
            if not existing_vibe:
                print(f"Seeding vibe: {vibe_data['name']}")
                new_vibe = Vibe(
                    id=str(uuid.uuid4()),
                    name=vibe_data["name"],
                    description=vibe_data["description"],
                    owner_id=admin_user.id
                )
                db.add(new_vibe)
                await db.commit()
                await db.refresh(new_vibe)
                
                # Add Admin as owner
                vibe_member = VibeMember(
                    vibe_id=new_vibe.id,
                    user_id=admin_user.id,
                    role="owner",
                    joined_at=datetime.datetime.utcnow()
                )
                db.add(vibe_member)
                await db.commit()
        
        print("Seeding complete. Starter vibes are locked in.")

if __name__ == "__main__":
    asyncio.run(seed_starter_vibes())
