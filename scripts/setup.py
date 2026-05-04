#!/usr/bin/env python3
"""
OmniNode Setup Script
Initializes the database and creates a demo user for testing.
"""

import sys
import os
import secrets

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.core.database import init_db, SessionLocal
from backend.models.models import User
from backend.core.security import get_password_hash


def generate_secret_key():
    """Generate a secure secret key."""
    return secrets.token_urlsafe(32)


def setup_database():
    """Initialize database and create tables."""
    print("🔧 Initializing database...")
    init_db()
    print("✅ Database tables created")


def create_demo_user():
    """Create a demo user for testing."""
    db = SessionLocal()
    
    # Check if demo user already exists
    existing_user = db.query(User).filter(User.username == "demo").first()
    if existing_user:
        print("ℹ️  Demo user already exists")
        db.close()
        return
    
    # Create demo user
    demo_user = User(
        username="demo",
        email="demo@omninode.local",
        hashed_password=get_password_hash("demo123"),
        is_active=True
    )
    
    db.add(demo_user)
    db.commit()
    db.refresh(demo_user)
    
    print(f"✅ Demo user created:")
    print(f"   Username: demo")
    print(f"   Password: demo123")
    print(f"   Email: {demo_user.email}")
    
    db.close()


def check_env_file():
    """Check if .env file exists and has necessary variables."""
    env_file = os.path.join(os.path.dirname(__file__), '..', '.env')
    env_example = os.path.join(os.path.dirname(__file__), '..', '.env.example')
    
    if not os.path.exists(env_file):
        print("⚠️  .env file not found")
        print("📝 Creating .env from .env.example...")
        
        # Copy example file
        with open(env_example, 'r') as f:
            content = f.read()
        
        # Generate new secret keys
        secret_key = generate_secret_key()
        encryption_key = generate_secret_key()
        
        # Replace placeholder values
        content = content.replace(
            'your-super-secret-key-change-in-production-min-32-chars',
            secret_key
        )
        content = content.replace(
            'your-encryption-key-change-in-production-32-chars',
            encryption_key
        )
        
        with open(env_file, 'w') as f:
            f.write(content)
        
        print("✅ .env file created with secure keys")
        print("⚠️  Review and update .env file with your settings")
    else:
        print("✅ .env file exists")


def print_next_steps():
    """Print next steps for the user."""
    print("\n" + "="*60)
    print("🎉 OmniNode Setup Complete!")
    print("="*60)
    print("\n📋 Next Steps:\n")
    print("1. Review your .env file:")
    print("   - Update CORS_ORIGINS if needed")
    print("   - Add any additional configuration")
    print("")
    print("2. Start the backend server:")
    print("   cd backend")
    print("   python main.py")
    print("   # Or: uvicorn main:app --reload")
    print("")
    print("3. In a new terminal, start the frontend:")
    print("   cd frontend")
    print("   npm install  # First time only")
    print("   npm run dev")
    print("")
    print("4. Access the application:")
    print("   Frontend: http://localhost:3000")
    print("   Backend API: http://localhost:8000")
    print("   API Docs: http://localhost:8000/docs")
    print("")
    print("5. Register your first MCP server:")
    print("   See docs/EXAMPLES.md for examples")
    print("")
    print("📚 Documentation:")
    print("   - README.md - Project overview")
    print("   - docs/ARCHITECTURE.md - Technical details")
    print("   - docs/DEVELOPMENT.md - Development guide")
    print("   - docs/EXAMPLES.md - Usage examples")
    print("")
    print("="*60)


def main():
    """Main setup function."""
    print("\n🌐 OmniNode Setup Wizard")
    print("="*60 + "\n")
    
    try:
        # Check environment file
        check_env_file()
        
        # Setup database
        setup_database()
        
        # Create demo user
        create_demo_user()
        
        # Print next steps
        print_next_steps()
        
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
