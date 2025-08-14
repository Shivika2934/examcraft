import json
import os
from openai import OpenAI

# Using OpenRouter API for AI model access
# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
openai = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

def generate_questions(subject, topic, difficulty, num_questions=10, question_type="multiple_choice"):
    """
    Generate exam questions using OpenAI API
    """
    try:
        # Create a comprehensive prompt for question generation
        prompt = f"""
        Generate {num_questions} {question_type} questions for an exam on the subject "{subject}" 
        with the topic "{topic}" at {difficulty} difficulty level.
        
        For each question, provide:
        1. Clear, well-formed question text
        2. Four answer options (A, B, C, D) for multiple choice questions
        3. The correct answer (A, B, C, or D)
        4. Ensure questions test understanding, not just memorization
        5. Make questions appropriate for {difficulty} level
        
        Return the response as a JSON object with this exact structure:
        {{
            "questions": [
                {{
                    "question_text": "Question text here",
                    "option_a": "Option A text",
                    "option_b": "Option B text", 
                    "option_c": "Option C text",
                    "option_d": "Option D text",
                    "correct_answer": "A",
                    "points": 1
                }}
            ]
        }}
        
        Make sure all questions are unique and cover different aspects of the topic.
        """
        
        response = openai.chat.completions.create(
            model="openai/gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert exam question generator. Create high-quality, educational questions that test student understanding effectively."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        if not content:
            raise Exception("Empty response from OpenAI API")
        result = json.loads(content)
        return result["questions"]
        
    except Exception as e:
        raise Exception(f"Failed to generate questions: {str(e)}")

def evaluate_subjective_answer(question, student_answer, correct_answer=None):
    """
    Evaluate subjective answers using AI
    """
    try:
        prompt = f"""
        Evaluate the following student answer for the given question:
        
        Question: {question}
        Student Answer: {student_answer}
        {f"Expected/Reference Answer: {correct_answer}" if correct_answer else ""}
        
        Please evaluate the answer on a scale of 0-100 and provide:
        1. A score (0-100)
        2. Brief feedback explaining the score
        3. Key points that were covered or missed
        
        Return as JSON:
        {{
            "score": 85,
            "feedback": "Good understanding shown but missing key concept X",
            "points_covered": ["Point 1", "Point 2"],
            "points_missed": ["Point 3"]
        }}
        """
        
        response = openai.chat.completions.create(
            model="openai/gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert educator evaluating student answers. Be fair but thorough in your assessment."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        if not content:
            raise Exception("Empty response from OpenAI API")
        return json.loads(content)
        
    except Exception as e:
        raise Exception(f"Failed to evaluate answer: {str(e)}")

def generate_question_variations(base_question, num_variations=3):
    """
    Generate variations of a question to prevent cheating
    """
    try:
        prompt = f"""
        Create {num_variations} variations of this question that test the same concept but with different wording, numbers, or examples:
        
        Original Question: {base_question['question_text']}
        Original Options:
        A) {base_question['option_a']}
        B) {base_question['option_b']}
        C) {base_question['option_c']}
        D) {base_question['option_d']}
        Correct Answer: {base_question['correct_answer']}
        
        For each variation, maintain the same difficulty level and learning objective.
        
        Return as JSON:
        {{
            "variations": [
                {{
                    "question_text": "Variation question text",
                    "option_a": "Option A",
                    "option_b": "Option B",
                    "option_c": "Option C", 
                    "option_d": "Option D",
                    "correct_answer": "B"
                }}
            ]
        }}
        """
        
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at creating question variations while maintaining educational value and difficulty."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        if not content:
            raise Exception("Empty response from OpenAI API")
        return json.loads(content)["variations"]
        
    except Exception as e:
        raise Exception(f"Failed to generate variations: {str(e)}")
