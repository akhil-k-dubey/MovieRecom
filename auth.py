import hashlib
from database import User, UserRating, get_db, init_db
from sqlalchemy.orm import Session

class AuthManager:
    def __init__(self):
        init_db()
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def user_exists(self, username):
        db = get_db()
        try:
            user = db.query(User).filter(User.username == username).first()
            return user is not None
        finally:
            db.close()
    
    def email_exists(self, email):
        db = get_db()
        try:
            user = db.query(User).filter(User.email == email).first()
            return user is not None
        finally:
            db.close()
    
    def create_user(self, username, password, email):
        if self.user_exists(username):
            return False, "Username already exists"
        
        if self.email_exists(email):
            return False, "Email already registered"
        
        db = get_db()
        try:
            new_user = User(
                username=username,
                password_hash=self.hash_password(password),
                email=email
            )
            db.add(new_user)
            db.commit()
            return True, "Account created successfully"
        except Exception as e:
            db.rollback()
            return False, f"Error creating account: {str(e)}"
        finally:
            db.close()
    
    def authenticate(self, username, password):
        db = get_db()
        try:
            user = db.query(User).filter(User.username == username).first()
            
            if not user:
                return False, "Username not found", None
            
            if self.hash_password(password) == user.password_hash:
                return True, "Login successful", user.id
            else:
                return False, "Incorrect password", None
        finally:
            db.close()
    
    def get_user_info(self, username):
        db = get_db()
        try:
            user = db.query(User).filter(User.username == username).first()
            if user:
                return {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'created_at': user.created_at
                }
            return None
        finally:
            db.close()
    
    def save_user_rating(self, user_id, movie_id, rating):
        db = get_db()
        try:
            existing_rating = db.query(UserRating).filter(
                UserRating.user_id == user_id,
                UserRating.movie_id == movie_id
            ).first()
            
            if existing_rating:
                existing_rating.rating = rating
            else:
                new_rating = UserRating(
                    user_id=user_id,
                    movie_id=movie_id,
                    rating=rating
                )
                db.add(new_rating)
            
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            return False
        finally:
            db.close()
    
    def get_user_ratings(self, user_id):
        db = get_db()
        try:
            ratings = db.query(UserRating).filter(UserRating.user_id == user_id).all()
            return {r.movie_id: r.rating for r in ratings}
        finally:
            db.close()
