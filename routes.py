from flask import session, render_template, request, redirect, url_for, flash, jsonify
from app import app, db
from replit_auth import require_login, require_admin, make_replit_blueprint
from flask_login import current_user
from models import User, Subject, Exam, Question, ExamSession, Answer
from ai_service import generate_questions, generate_question_variations
from exam_service import (
    create_exam_session, get_randomized_questions, submit_answer,
    finish_exam_session, get_exam_time_remaining, get_student_exam_history,
    get_exam_statistics
)
from datetime import datetime
import logging

app.register_blueprint(make_replit_blueprint(), url_prefix="/auth")

# Make session permanent
@app.before_request
def make_session_permanent():
    session.permanent = True

@app.route('/')
def index():
    """Landing page - redirect based on user role"""
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('student_dashboard'))
    
    return render_template('index.html')

@app.route('/admin/login')
def admin_login():
    """Admin login - sets role preference and redirects to auth"""
    session['role_preference'] = 'admin'
    return redirect(url_for('replit_auth.login'))

@app.route('/student/login')  
def student_login():
    """Student login - sets role preference and redirects to auth"""
    session['role_preference'] = 'student'
    return redirect(url_for('replit_auth.login'))

@app.route('/switch-to-admin')
@require_login
def switch_to_admin():
    """Switch current user to admin role (for demo purposes)"""
    current_user.role = 'admin'
    db.session.commit()
    flash('You are now an administrator!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/switch-to-student')
@require_login  
def switch_to_student():
    """Switch current user to student role"""
    current_user.role = 'student'
    db.session.commit()
    flash('You are now a student!', 'info')
    return redirect(url_for('student_dashboard'))

@app.route('/admin/users')
@require_admin
def manage_users():
    """Admin interface to manage users"""
    users = User.query.order_by(User.id).all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/users/<user_id>/toggle-role', methods=['POST'])
@require_admin
def toggle_user_role(user_id):
    """Toggle user role between admin and student"""
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('You cannot change your own role!', 'error')
        return redirect(url_for('manage_users'))
    
    # Toggle role
    user.role = 'student' if user.role == 'admin' else 'admin'
    db.session.commit()
    
    flash(f'User {user.first_name or user.email} is now a {user.role}!', 'success')
    return redirect(url_for('manage_users'))

# Admin Routes
@app.route('/admin')
@require_admin
def admin_dashboard():
    """Admin dashboard with exam management"""
    exams = Exam.query.filter_by(creator_id=current_user.id).order_by(Exam.created_at.desc()).all()
    subjects = Subject.query.all()
    
    # Get statistics for each exam
    exam_stats = {}
    for exam in exams:
        exam_stats[exam.id] = get_exam_statistics(exam.id)
    
    # Get user statistics
    total_users = User.query.count()
    admin_users = User.query.filter_by(role='admin').count()
    student_users = User.query.filter_by(role='student').count()
    
    return render_template('admin/dashboard.html', 
                         exams=exams, 
                         subjects=subjects, 
                         exam_stats=exam_stats,
                         total_users=total_users,
                         admin_users=admin_users,
                         student_users=student_users)

@app.route('/admin/create-exam', methods=['GET', 'POST'])
@require_admin
def create_exam():
    """Create a new exam"""
    if request.method == 'POST':
        try:
            # Get form data
            title = request.form.get('title')
            description = request.form.get('description')
            subject_name = request.form.get('subject')
            topic = request.form.get('topic')
            difficulty = request.form.get('difficulty')
            duration = int(request.form.get('duration', 60))
            num_questions = int(request.form.get('num_questions', 10))
            
            # Create or get subject
            subject = Subject.query.filter_by(name=subject_name).first()
            if not subject:
                subject = Subject()
                subject.name = subject_name
                db.session.add(subject)
                db.session.commit()
            
            # Create exam
            exam = Exam()
            exam.title = title
            exam.description = description
            exam.subject_id = subject.id
            exam.creator_id = current_user.id
            exam.difficulty_level = difficulty
            exam.duration_minutes = duration
            exam.total_questions = num_questions
            
            db.session.add(exam)
            db.session.commit()
            
            # Generate questions using AI
            try:
                ai_questions = generate_questions(
                    subject=subject_name,
                    topic=topic,
                    difficulty=difficulty,
                    num_questions=num_questions
                )
                
                # Save questions to database
                for i, q_data in enumerate(ai_questions):
                    question = Question()
                    question.exam_id = exam.id
                    question.question_text = q_data['question_text']
                    question.option_a = q_data['option_a']
                    question.option_b = q_data['option_b']
                    question.option_c = q_data['option_c']
                    question.option_d = q_data['option_d']
                    question.correct_answer = q_data['correct_answer']
                    question.points = q_data.get('points', 1)
                    question.order_index = i
                    db.session.add(question)
                
                db.session.commit()
                flash('Exam created successfully with AI-generated questions!', 'success')
                return redirect(url_for('admin_dashboard'))
                
            except Exception as e:
                logging.error(f"Error generating questions: {str(e)}")
                flash(f'Exam created but failed to generate questions: {str(e)}', 'warning')
                return redirect(url_for('admin_dashboard'))
                
        except Exception as e:
            logging.error(f"Error creating exam: {str(e)}")
            flash(f'Error creating exam: {str(e)}', 'error')
    
    subjects = Subject.query.all()
    return render_template('admin/create_exam.html', subjects=subjects)

@app.route('/admin/exam/<int:exam_id>/publish')
@require_admin
def publish_exam(exam_id):
    """Publish an exam to make it available to students"""
    exam = Exam.query.get_or_404(exam_id)
    
    if exam.creator_id != current_user.id:
        flash('You can only publish your own exams.', 'error')
        return redirect(url_for('admin_dashboard'))
    
    exam.is_published = True
    db.session.commit()
    
    flash(f'Exam "{exam.title}" has been published and is now available to students.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/exam/<int:exam_id>/unpublish')
@require_admin
def unpublish_exam(exam_id):
    """Unpublish an exam"""
    exam = Exam.query.get_or_404(exam_id)
    
    if exam.creator_id != current_user.id:
        flash('You can only unpublish your own exams.', 'error')
        return redirect(url_for('admin_dashboard'))
    
    exam.is_published = False
    db.session.commit()
    
    flash(f'Exam "{exam.title}" has been unpublished.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/exam/<int:exam_id>/regenerate-questions')
@require_admin  
def regenerate_questions(exam_id):
    """Regenerate questions for an exam that has none"""
    exam = Exam.query.get_or_404(exam_id)
    
    if exam.creator_id != current_user.id:
        flash('You can only regenerate questions for your own exams.', 'error')
        return redirect(url_for('admin_dashboard'))
    
    try:
        # Delete existing questions
        Question.query.filter_by(exam_id=exam_id).delete()
        
        # Generate new questions using AI
        ai_questions = generate_questions(
            subject=exam.subject.name,
            topic=exam.description or exam.title,
            difficulty=exam.difficulty_level,
            num_questions=exam.total_questions
        )
        
        # Save questions to database
        for i, q_data in enumerate(ai_questions):
            question = Question()
            question.exam_id = exam.id
            question.question_text = q_data['question_text']
            question.option_a = q_data['option_a']
            question.option_b = q_data['option_b']
            question.option_c = q_data['option_c']
            question.option_d = q_data['option_d']
            question.correct_answer = q_data['correct_answer']
            question.points = q_data.get('points', 1)
            question.order_index = i
            db.session.add(question)
        
        db.session.commit()
        flash(f'Successfully regenerated {len(ai_questions)} questions for "{exam.title}"!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Failed to regenerate questions: {str(e)}', 'error')
        logging.error(f"Error regenerating questions: {str(e)}")
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/exam/<int:exam_id>/results')
@require_admin
def view_exam_results(exam_id):
    """View results for an exam"""
    exam = Exam.query.get_or_404(exam_id)
    
    if exam.creator_id != current_user.id:
        flash('You can only view results for your own exams.', 'error')
        return redirect(url_for('admin_dashboard'))
    
    sessions = ExamSession.query.filter_by(
        exam_id=exam_id,
        is_submitted=True
    ).order_by(ExamSession.score.desc()).all()
    
    stats = get_exam_statistics(exam_id)
    
    return render_template('admin/view_results.html', exam=exam, sessions=sessions, stats=stats)

# Student Routes
@app.route('/student')
@require_login
def student_dashboard():
    """Student dashboard with available exams"""
    # Get published exams
    available_exams = Exam.query.filter_by(is_published=True, is_active=True).all()
    
    # Get student's exam history
    exam_history = get_student_exam_history(current_user.id)
    
    # Get active exam sessions
    active_sessions = ExamSession.query.filter_by(
        student_id=current_user.id,
        is_submitted=False
    ).all()
    
    return render_template('student/dashboard.html', 
                         available_exams=available_exams, 
                         exam_history=exam_history,
                         active_sessions=active_sessions)

@app.route('/student/exam/<int:exam_id>/start')
@require_login
def start_exam(exam_id):
    """Start an exam"""
    exam = Exam.query.get_or_404(exam_id)
    
    if not exam.is_published or not exam.is_active:
        flash('This exam is not available.', 'error')
        return redirect(url_for('student_dashboard'))
    
    # Check if student already has a submitted session for this exam
    existing_session = ExamSession.query.filter_by(
        exam_id=exam_id,
        student_id=current_user.id,
        is_submitted=True
    ).first()
    
    if existing_session:
        flash('You have already completed this exam.', 'warning')
        return redirect(url_for('student_dashboard'))
    
    # Create or get active session
    exam_session = create_exam_session(exam_id, current_user.id)
    
    return redirect(url_for('take_exam', session_id=exam_session.id))

@app.route('/student/exam/session/<int:session_id>')
@require_login
def take_exam(session_id):
    """Take an exam"""
    exam_session = ExamSession.query.get_or_404(session_id)
    
    if exam_session.student_id != current_user.id:
        flash('You can only access your own exam sessions.', 'error')
        return redirect(url_for('student_dashboard'))
    
    if exam_session.is_submitted:
        flash('This exam has already been submitted.', 'info')
        return redirect(url_for('view_results', session_id=session_id))
    
    # Check if time is up
    time_remaining = get_exam_time_remaining(exam_session)
    if time_remaining <= 0:
        flash('Time is up! Your exam has been automatically submitted.', 'warning')
        return redirect(url_for('view_results', session_id=session_id))
    
    # Get randomized questions for this student
    questions = get_randomized_questions(exam_session.exam_id, current_user.id)
    
    # Get existing answers
    existing_answers = {}
    answers = Answer.query.filter_by(exam_session_id=session_id).all()
    for answer in answers:
        existing_answers[answer.question_id] = answer.student_answer
    
    return render_template('student/exam.html', 
                         exam_session=exam_session,
                         questions=questions,
                         existing_answers=existing_answers,
                         time_remaining=time_remaining)

@app.route('/student/exam/session/<int:session_id>/submit-answer', methods=['POST'])
@require_login
def submit_exam_answer(session_id):
    """Submit an answer for a question"""
    exam_session = ExamSession.query.get_or_404(session_id)
    
    if exam_session.student_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if exam_session.is_submitted:
        return jsonify({'error': 'Exam already submitted'}), 400
    
    if not request.json:
        return jsonify({'error': 'Invalid request format'}), 400
    
    question_id = request.json.get('question_id')
    student_answer = request.json.get('answer')
    
    try:
        submit_answer(session_id, question_id, student_answer)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/student/exam/session/<int:session_id>/submit', methods=['POST'])
@require_login
def submit_exam(session_id):
    """Submit the entire exam"""
    exam_session = ExamSession.query.get_or_404(session_id)
    
    if exam_session.student_id != current_user.id:
        flash('You can only submit your own exam sessions.', 'error')
        return redirect(url_for('student_dashboard'))
    
    if exam_session.is_submitted:
        flash('This exam has already been submitted.', 'info')
        return redirect(url_for('view_results', session_id=session_id))
    
    # Submit any pending answers from the form
    for key, value in request.form.items():
        if key.startswith('question_'):
            question_id = int(key.replace('question_', ''))
            if value:
                submit_answer(session_id, question_id, value)
    
    # Finish the exam session
    finish_exam_session(session_id)
    
    flash('Exam submitted successfully!', 'success')
    return redirect(url_for('view_results', session_id=session_id))

@app.route('/student/exam/session/<int:session_id>/results')
@require_login
def view_results(session_id):
    """View exam results"""
    exam_session = ExamSession.query.get_or_404(session_id)
    
    if exam_session.student_id != current_user.id:
        flash('You can only view your own exam results.', 'error')
        return redirect(url_for('student_dashboard'))
    
    if not exam_session.is_submitted:
        flash('This exam has not been submitted yet.', 'warning')
        return redirect(url_for('take_exam', session_id=session_id))
    
    # Get questions and answers
    questions = Question.query.filter_by(exam_id=exam_session.exam_id).all()
    answers = Answer.query.filter_by(exam_session_id=session_id).all()
    
    # Create answer lookup
    answer_lookup = {answer.question_id: answer for answer in answers}
    
    return render_template('student/results.html', 
                         exam_session=exam_session,
                         questions=questions,
                         answer_lookup=answer_lookup)

@app.route('/admin/make-admin/<user_id>')
@require_admin
def make_admin(user_id):
    """Make a user an admin - for development purposes"""
    user = User.query.get_or_404(user_id)
    user.role = 'admin'
    db.session.commit()
    flash(f'User {user.email} is now an admin.', 'success')
    return redirect(url_for('admin_dashboard'))

# API Routes for AJAX calls
@app.route('/api/exam/session/<int:session_id>/time-remaining')
@require_login
def get_time_remaining(session_id):
    """Get remaining time for an exam session"""
    exam_session = ExamSession.query.get_or_404(session_id)
    
    if exam_session.student_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    time_remaining = get_exam_time_remaining(exam_session)
    
    return jsonify({
        'time_remaining': time_remaining,
        'is_submitted': exam_session.is_submitted
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500
