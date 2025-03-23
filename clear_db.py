from app import db, app  
from sqlalchemy.sql import text  # Import text()

def clear_database():
    with app.app_context():
        db.session.execute(text("DELETE FROM user;"))
        db.session.execute(text("DELETE FROM teacher;"))
        db.session.execute(text("DELETE FROM student;"))
        db.session.execute(text("DELETE FROM subject;"))
        db.session.execute(text("DELETE FROM chapter;"))
        db.session.execute(text("DELETE FROM quiz;"))
        db.session.execute(text("DELETE FROM question;"))
        db.session.execute(text("DELETE FROM student_quiz_attempt;"))
        db.session.execute(text("DELETE FROM result;"))
        db.session.commit()
        print("Database cleared!")

if __name__ == "__main__":
    clear_database()
