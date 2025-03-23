from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db, User, Teacher, Subject, Chapter, Quiz, Question, StudentQuizAttempt, Result , Student
from flask import get_flashed_messages

app = Flask(__name__)
app.secret_key = "3d90b2b1e96fbdf2c77e62f95924773a18cbf72ee66fe0c40efff3026c7e3a34"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/student')
def student():
    return render_template('student.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        if not name or not email or not password:
            return "Missing data!", 400

        existing_user = Student.query.filter_by(email=email).first()
        if existing_user:
            return "User already exists!", 400

        new_user = Student(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        session['student_email'] = new_user.email  # ✅ Store email for dashboard check
        return redirect(url_for('dashboard'))

    return render_template('signup.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        student = Student.query.filter_by(email=email).first()
        
        print(f"Trying to sign in: {email}")  # Debugging
        
        if student:
            print(f"Student found: {student.name}, Password match: {student.password == password}")  # Debugging
            
            if student.password == password:  # Add hashing later
                session.permanent = True  # Keep session alive
                session['user_id'] = student.id  # Store user ID in session
                session['student_email'] = student.email  # Store email in session
                flash("Login successful!", "success")
                return redirect(url_for('dashboard'))
        
        flash("Invalid credentials!", "error")
    
    return render_template('signin.html')

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:  # Use `user_id` instead of `student_email`
        return redirect(url_for("signin"))

    student = Student.query.get(session["user_id"])  # Fetch student by ID
    if not student:
        return redirect(url_for("signin"))

    subjects = Subject.query.all()
    quizzes = Quiz.query.all()
    quiz_history = StudentQuizAttempt.query.filter_by(student_id=student.id).all()

    return render_template(
        "dashboard.html",
        subjects=subjects,
        quizzes=quizzes,
        quiz_history=quiz_history,
    )



@app.route('/teacher_login', methods=['GET', 'POST'])
def teacher_login():
    if request.method == 'POST':
        session['teacher'] = request.form.get('email')
        return redirect(url_for('teacher_dashboard'))

    return render_template('teacher_login.html')

@app.route('/teacher_dashboard')
def teacher_dashboard():
    if 'teacher' not in session:
        return redirect(url_for('teacher_login')) 
    subjects = Subject.query.all()
    quizzes = Quiz.query.all()
    return render_template('teacher_dashboard.html', subjects=subjects, quizzes=quizzes)

@app.route('/search_quiz')
def search_quiz():
    query = request.args.get('q', '').strip().lower()
    print(f"Search Query: {query}")  # ✅ Debugging

    quizzes = Quiz.query.filter(Quiz.title.ilike(f"%{query}%")).all()
    print(f"Found Quizzes: {[quiz.title for quiz in quizzes]}")  # ✅ Debugging

    results = []
    for quiz in quizzes:
        if 'teacher' in session:
            url = url_for('view_quiz', chapter_id=quiz.chapter_id)
        else:
            url = url_for('attempt_quiz', quiz_id=quiz.id)

        results.append({"title": quiz.title, "url": url})

    print(f"Final JSON Response: {results}")  # ✅ Debugging
    return jsonify(results)


@app.route('/add_subject', methods=['GET', 'POST'])
def add_subject():
    if request.method == 'POST':
        new_subject = Subject(
            name=request.form['name'], 
            description=request.form['description']
        )
        db.session.add(new_subject)
        db.session.commit()
        return redirect(url_for('teacher_dashboard'))

    return render_template('add_subject.html')

@app.route('/add_chapter/<int:subject_id>', methods=['GET', 'POST'])
def add_chapter(subject_id):
    subject = Subject.query.get(subject_id)

    if not subject:
        flash("Subject not found!", "error")
        return redirect(url_for('teacher_dashboard'))

    if request.method == 'POST':
        chapter_name = request.form.get('chapter_name')
        chapter_desc = request.form.get('chapter_desc')

        if not chapter_name or not chapter_desc:
            flash("Chapter name and description cannot be empty!", "warning")
            return redirect(url_for('add_chapter', subject_id=subject_id))

        new_chapter = Chapter(name=chapter_name, description=chapter_desc, subject_id=subject_id)
        db.session.add(new_chapter)
        db.session.commit()

        flash("Chapter added successfully!", "success")
        return redirect(url_for('add_chapter', subject_id=subject_id))

    chapters = Chapter.query.filter_by(subject_id=subject_id).all()
    return render_template('add_chapter.html', subject=subject, chapters=chapters)

@app.route('/add_quiz/<int:chapter_id>', methods=['GET', 'POST'])
@app.route('/add_quiz/<int:chapter_id>/<int:quiz_id>', methods=['GET', 'POST'])
def add_quiz(chapter_id, quiz_id=None):
    chapter = Chapter.query.get_or_404(chapter_id)
    quiz = Quiz.query.get(quiz_id) if quiz_id else None
    questions = Question.query.filter_by(quiz_id=quiz_id).all() if quiz else []
    
    subject_id = chapter.subject_id  # ✅ Get subject ID
    subject_name = Subject.query.get(subject_id).name  # Optional: Get subject name

    get_flashed_messages()

    if request.method == 'POST':
        print("DEBUG: Received form data:", request.form)  # Debugging line

        title = request.form.get('title', '').strip()
        
        if not title: 
            flash("Quiz title is required!", "error")
            return redirect(url_for('add_quiz', chapter_id=chapter_id, quiz_id=quiz_id))

        if quiz is None:
            quiz = Quiz(title=title, chapter_id=chapter_id)  # ✅ No duration
            db.session.add(quiz)
            db.session.commit()
        else:
            quiz.title = title  # ✅ No duration update
            db.session.commit()

        for i in range(1, 11):
            q_text = request.form.get(f'question_{i}', '').strip()
            if not q_text:
                continue  

            option_a = request.form.get(f'option_{i}_a')
            option_b = request.form.get(f'option_{i}_b')
            option_c = request.form.get(f'option_{i}_c')
            option_d = request.form.get(f'option_{i}_d')

            correct_answer = request.form.get(f'correct_{i}')
            if not correct_answer:
                flash(f"Error: Question {i} must have a correct option!", "error")
                return redirect(url_for('add_quiz', chapter_id=chapter_id, quiz_id=quiz_id))

            question = Question.query.filter_by(id=request.form.get(f'question_id_{i}')).first()
            if not question:
                question = Question(quiz_id=quiz.id)

            question.text = q_text
            question.option1 = option_a
            question.option2 = option_b
            question.option3 = option_c
            question.option4 = option_d
            question.correct_option = correct_answer
            db.session.add(question)

        db.session.commit()
        flash("Quiz saved successfully!", "success")
        return redirect(url_for('view_quiz', chapter_id=chapter_id))

    return render_template(
        "add_quiz.html", 
        chapter=chapter, 
        quiz=quiz, 
        questions=questions,
        subject_id=subject_id,  # ✅ Now `subject_id` is available in the template
        subject_name=subject_name  # Optional
    )


@app.route('/view_quiz/<int:chapter_id>')
def view_quiz(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
    return render_template('view_quiz.html', chapter=chapter, quizzes=quizzes)

@app.route("/attempt_quiz/<int:quiz_id>", methods=["GET", "POST"])
def attempt_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()

    if "user_id" not in session:
        flash("Please log in to attempt the quiz!", "error")
        return redirect(url_for("signin"))

    student = Student.query.get(session["user_id"])

    if request.method == "POST":
        total_questions = len(questions)
        correct_answers = 0

        for question in questions:
            selected_answer = request.form.get(f"question_{question.id}")

            correct_option_text = None
            if question.correct_option == "a":
                correct_option_text = question.option1
            elif question.correct_option == "b":
                correct_option_text = question.option2
            elif question.correct_option == "c":
                correct_option_text = question.option3
            elif question.correct_option == "d":
                correct_option_text = question.option4

            if selected_answer == correct_option_text:
                correct_answers += 1

        score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0

        # Save the attempt in StudentQuizAttempt
        new_attempt = StudentQuizAttempt(student_id=student.id, quiz_id=quiz_id, score=score)
        db.session.add(new_attempt)
        db.session.commit()

        flash(f"Your Score: {score:.1f}%", "success")

        return redirect(url_for("student_result", student_name=student.name, quiz_id=quiz_id, score=score))

    return render_template("attempt_quiz.html", quiz=quiz, questions=questions)



@app.route("/student_result/<string:student_name>/<int:quiz_id>")
def student_result(student_name, quiz_id):
    score = request.args.get("score", type=float)
    if score is None:
        flash("Invalid request. No score found!", "error")
        return redirect(url_for("dashboard"))

    return render_template("student_result.html", student_name=student_name, score=score)




@app.route("/student/chapters/<int:subject_id>")
def view_student_chapters(subject_id):
    chapters = Chapter.query.filter_by(subject_id=subject_id).all()
    return render_template("student_chapters.html", chapters=chapters)

@app.route('/student/quizzes/<int:chapter_id>')
def view_student_quizzes(chapter_id):
    quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
    
   
    chapter = Chapter.query.get(chapter_id)
    subject_id = chapter.subject_id if chapter else None 
    
    return render_template("student_quizzes.html", quizzes=quizzes, subject_id=subject_id)

@app.route("/quiz_stats/<int:quiz_id>")
def quiz_stats(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    
    
    attempts = StudentQuizAttempt.query.filter_by(quiz_id=quiz_id).all()

    return render_template("quiz_stats.html", quiz=quiz, attempts=attempts)



@app.route('/delete_subject/<int:subject_id>')
def delete_subject(subject_id):
    if 'teacher' not in session:
        return redirect(url_for('teacher_login')) 

    subject = Subject.query.get_or_404(subject_id)

    for chapter in subject.chapters:
        for quiz in chapter.quizzes:
            Question.query.filter_by(quiz_id=quiz.id).delete()
            db.session.delete(quiz)
        db.session.delete(chapter)

    db.session.delete(subject)
    db.session.commit()
    
    return redirect(url_for('teacher_dashboard'))

@app.route('/delete_chapter/<int:chapter_id>')
def delete_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    db.session.delete(chapter)
    db.session.commit()
    flash("Chapter deleted successfully!", "success")
    return redirect(url_for('teacher_dashboard'))

@app.route("/student_history")
def student_history():
    if "user_id" not in session:
        return redirect(url_for("signin"))

    student = Student.query.get(session["user_id"])
    if not student:
        flash("Student not found!", "error")
        return redirect(url_for("dashboard"))

    attempts = StudentQuizAttempt.query.filter_by(student_id=student.id).all()

    print("DEBUG: Quiz attempts found:", attempts)  # Print attempts for debugging
    for attempt in attempts:
        print(f"Quiz: {attempt.quiz.title}, Score: {attempt.score}, Date: {attempt.timestamp}")

    return render_template("history.html", quiz_attempts=attempts)

@app.route('/manage_users')
def manage_users():
    students = Student.query.all()  
    
    print("Students:", students)
    return render_template('manage_users.html', users=students) 




@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    student = Student.query.get(user_id) 

    if student:
        db.session.delete(student)
        db.session.commit()
        return jsonify({"success": True})

    return jsonify({"success": False, "message": "Student not found"})




@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
