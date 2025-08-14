from datetime import datetime, timedelta
from app import db
from models import Exam, Question, ExamSession, Answer, Subject, User
import random

def create_exam_session(exam_id, student_id):
    """
    Create a new exam session for a student
    """
    # Check if student already has an active session for this exam
    existing_session = ExamSession.query.filter_by(
        exam_id=exam_id,
        student_id=student_id,
        is_submitted=False
    ).first()
    
    if existing_session:
        return existing_session
    
    # Create new session
    exam_session = ExamSession()
    exam_session.exam_id = exam_id
    exam_session.student_id = student_id
    exam_session.start_time = datetime.now()
    
    db.session.add(exam_session)
    db.session.commit()
    
    return exam_session

def get_randomized_questions(exam_id, student_id):
    """
    Get questions for an exam, randomized per student to prevent cheating
    """
    questions = Question.query.filter_by(exam_id=exam_id).order_by(Question.order_index).all()
    
    # Create a deterministic but unique shuffle based on student_id
    random.seed(hash(str(student_id) + str(exam_id)) % (2**32))
    randomized_questions = questions.copy()
    random.shuffle(randomized_questions)
    
    # Reset random seed
    random.seed()
    
    return randomized_questions

def submit_answer(exam_session_id, question_id, student_answer):
    """
    Submit an answer for a question in an exam session
    """
    # Check if answer already exists
    existing_answer = Answer.query.filter_by(
        exam_session_id=exam_session_id,
        question_id=question_id
    ).first()
    
    if existing_answer:
        existing_answer.student_answer = student_answer
    else:
        answer = Answer()
        answer.exam_session_id = exam_session_id
        answer.question_id = question_id
        answer.student_answer = student_answer
        db.session.add(answer)
    
    db.session.commit()

def evaluate_exam_session(exam_session_id):
    """
    Evaluate all answers in an exam session
    """
    exam_session = ExamSession.query.get(exam_session_id)
    if not exam_session:
        return False
    
    answers = Answer.query.filter_by(exam_session_id=exam_session_id).all()
    total_points = 0
    earned_points = 0
    
    for answer in answers:
        question = Question.query.get(answer.question_id)
        if not question:
            continue  # Skip if question not found
            
        total_points += question.points
        
        # Auto-evaluate objective questions
        if question.question_type == 'multiple_choice':
            if answer.student_answer and answer.student_answer.upper() == question.correct_answer.upper():
                answer.is_correct = True
                answer.points_earned = question.points
                earned_points += question.points
            else:
                answer.is_correct = False
                answer.points_earned = 0
        
        # For subjective questions, manual evaluation needed
        # For now, mark as requiring manual review
        elif question.question_type in ['short_answer', 'essay']:
            answer.is_correct = None  # Pending manual review
            answer.points_earned = 0  # Will be updated after manual review
    
    # Update exam session with results
    exam_session.total_points = total_points
    exam_session.score = (earned_points / total_points * 100) if total_points > 0 else 0
    exam_session.is_evaluated = True
    exam_session.end_time = datetime.now()
    
    db.session.commit()
    
    return True

def finish_exam_session(exam_session_id):
    """
    Mark an exam session as completed and evaluate it
    """
    exam_session = ExamSession.query.get(exam_session_id)
    if not exam_session:
        return False
    
    exam_session.is_submitted = True
    exam_session.end_time = datetime.now()
    
    db.session.commit()
    
    # Auto-evaluate the session
    evaluate_exam_session(exam_session_id)
    
    return True

def get_exam_time_remaining(exam_session):
    """
    Calculate remaining time for an exam session
    """
    if exam_session.is_submitted:
        return 0
    
    exam = exam_session.exam
    elapsed_time = datetime.now() - exam_session.start_time
    total_duration = timedelta(minutes=exam.duration_minutes)
    
    remaining = total_duration - elapsed_time
    
    if remaining.total_seconds() <= 0:
        # Time's up, auto-submit
        finish_exam_session(exam_session.id)
        return 0
    
    return int(remaining.total_seconds())

def get_student_exam_history(student_id):
    """
    Get all completed exams for a student
    """
    sessions = ExamSession.query.filter_by(
        student_id=student_id,
        is_submitted=True
    ).order_by(ExamSession.created_at.desc()).all()
    
    return sessions

def get_exam_statistics(exam_id):
    """
    Get statistics for an exam
    """
    sessions = ExamSession.query.filter_by(
        exam_id=exam_id,
        is_submitted=True,
        is_evaluated=True
    ).all()
    
    if not sessions:
        return {
            'total_attempts': 0,
            'average_score': 0,
            'highest_score': 0,
            'lowest_score': 0,
            'pass_rate': 0
        }
    
    scores = [session.score for session in sessions]
    pass_count = len([score for score in scores if score >= 60])  # Assuming 60% is passing
    
    return {
        'total_attempts': len(sessions),
        'average_score': sum(scores) / len(scores),
        'highest_score': max(scores),
        'lowest_score': min(scores),
        'pass_rate': (pass_count / len(sessions)) * 100
    }
