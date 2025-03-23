from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# User Model (Not directly used in relationships)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<User {self.id}: {self.email}>"

# Teacher Model
class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Student Model
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    # Relationship with quiz attempts
    quiz_attempts = db.relationship('StudentQuizAttempt', back_populates='student', lazy=True, cascade="all, delete-orphan")

# Subject Model
class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)

    # Relationship with Chapters (One Subject → Many Chapters)
    chapters = db.relationship('Chapter', back_populates='subject', lazy=True, cascade="all, delete-orphan")

# Chapter Model
class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id', name='fk_chapter_subject'), nullable=False)

    # Relationship with Subject & Quizzes
    subject = db.relationship('Subject', back_populates='chapters')
    quizzes = db.relationship('Quiz', back_populates='chapter', lazy=True, cascade="all, delete-orphan")

# Quiz Model
class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)

    # Relationship with Questions & Student Attempts
    chapter = db.relationship('Chapter', back_populates='quizzes')
    questions = db.relationship('Question', back_populates='quiz', lazy=True, cascade="all, delete-orphan")
    quiz_attempts = db.relationship('StudentQuizAttempt', back_populates='quiz', lazy=True, cascade="all, delete-orphan")
    results = db.relationship('Result', back_populates='quiz', lazy=True, cascade="all, delete-orphan")

# Question Model
class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    text = db.Column(db.String(255), nullable=False)
    option1 = db.Column(db.String(255), nullable=True) 
    option2 = db.Column(db.String(255), nullable=True)  
    option3 = db.Column(db.String(255), nullable=True)  
    option4 = db.Column(db.String(255), nullable=True)  
    correct_option = db.Column(db.String(255), nullable=False)  # Cannot be NULL

    # Relationship with Quiz
    quiz = db.relationship('Quiz', back_populates='questions')

# Student Quiz Attempt Model
class StudentQuizAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id', name='fk_studentquizattempt_student'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id', name='fk_studentquizattempt_quiz'), nullable=False)
    score = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)  # ✅ Fix: Renamed correctly

    # Fixed Relationships
    student = db.relationship('Student', back_populates='quiz_attempts')
    quiz = db.relationship('Quiz', back_populates='quiz_attempts')

# Result Model
class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quiz.id"), nullable=False)
    score = db.Column(db.Float, nullable=False)

    # Relationship with Quiz
    quiz = db.relationship("Quiz", back_populates="results")
