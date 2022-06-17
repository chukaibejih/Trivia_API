import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10 # default number of questions per page

def paginated_questions(request, selection):     
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    question = [question.format() for question in selection]
    current_questions = question[start:end]

    return current_questions

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    cors = CORS(app, resources={r"/*": {"origins": "*"}}) # r"/*" means all routes

  
    # after_request decorator to set Access-Control-Allow
  
    @app.after_request 
    def after_request(response): 
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    """
    Created an endpoint to handle GET requests for all available categories.
    """
    @app.route('/categories')
    def get_categories():
        try:
            categories = Category.query.all()
            categories_list = {category.id: category.type for category in categories}
            return jsonify({
                'success': True,
                'categories': categories_list
            })
        except Exception as e:
            print(e)
            abort(404)



    """
    Created an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.
    """
    @app.route('/questions')
    def get_questions():
        try:
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginated_questions(request, selection)
            categories = Category.query.all()
            categories_list = {category.id: category.type for category in categories}
            # if len(current_questions) == 0:
            #     abort(404)
            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(Question.query.all()),
                'categories': categories_list,
                'current_category': None
            })
        except Exception as e:
            print(e)
            abort(404)


    # Created an endpoint to DELETE question using a question ID.

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()

            if question is None:
                abort(404)
            question.delete()
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginated_questions(request, selection)
            return jsonify({
                'success': True,
                'deleted': question_id,
                'questions': current_questions,
                'total_questions': len(Question.query.all())
            })
        except Exception as e:
            print(e)
            abort(422)

    """
    Created an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.
    """
    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()
        new_question = body.get('question')
        new_answer = body.get('answer')
        new_category = body.get('category')
        new_difficulty = body.get('difficulty')
        try:
            question = Question(question=new_question, 
                                answer=new_answer, 
                                category=new_category, 
                                difficulty=new_difficulty)
            question.insert()

            selection = Question.query.order_by(Question.id).all()
            current_questions = paginated_questions(request, selection)
            return jsonify({
                'success': True,
                'created': question.id,
                'questions': current_questions,
                'total_questions': len(Question.query.all())
            })
        except Exception as e:
            print(e)
            abort(400)
        

    """
    Created a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.
    """
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        try:
            body = request.get_json()
            search_term = body.get('searchTerm')
            selection = Question.query.filter(Question.question.ilike('%' + search_term + '%')).all()
            current_questions = paginated_questions(request, selection)
            categories = Category.query.all()
            categories_list = [category.format() for category in categories]
            if len(current_questions) == 0:
                abort(404)
            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(Question.query.all()),
                'categories': categories_list,
                'current_category': None
            })
        except Exception as e:
            print(e)
            abort(422)

    # Create a GET endpoint to get questions based on category.

    @app.route('/categories/<int:category_id>/questions')
    def get_category_questions(category_id):
        try:
            category = Category.query.get(category_id)
            questions = Question.query.filter(Question.category == category.id).all()
            current_questions = paginated_questions(request, questions)
            categories = Category.query.all()
            categories_list = [category.format() for category in categories]
            if len(current_questions) == 0:
                abort(404)

            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(Question.query.all()),
                'categories': categories_list,
                'current_category': category.type
            })
        except Exception as e:
            print(e)
            abort(404)
        

    """
    Created a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.
    """
    @app.route('/quizzes', methods=['POST'])
    def get_quiz_questions():
        try:
            body = request.get_json()
            previous_questions = body.get('previous_questions')
            quiz_category = body.get('quiz_category')
            if quiz_category['id'] == 0:
                questions = Question.query.all()
            else:
                questions = Question.query.filter(Question.category == quiz_category['id']).all()
            quiz_questions = []
            for question in questions:
                if question.id not in previous_questions:
                    quiz_questions.append(question)
            if len(quiz_questions) == 0:
                abort(404)
            random_question = random.choice(quiz_questions)
            return jsonify({
                'success': True,
                'question': random_question.format()
            })
        except Exception as e:
            print(e)
            abort(422)

    """
    Created error handlers for all expected errors
    including 404 and 422.
    """

    @app.errorhandler(404)
    def not_found(error):
        return jsonify ({
            "success": False,
            "error": 404,
            "message": "resource not found"
        })

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify ({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        })

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify ({
            "success": False,
            "error": 400,
            "message": "bad request"
        })

    return app

