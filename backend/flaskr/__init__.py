import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,PATCH ,OPTIONS')
    return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories', methods=['GET'])
  def get_categories():
    categories = Category.query.order_by(Category.id).all()
    if categories is None:
      abort(404)
      

    categories_list = []
    for category in categories:
        categories_list.append(category.type)


    return jsonify({
      'success': True,
      'categories': categories_list })


  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions', methods=['GET'])
  def get_questions():
      questions = Question.query.order_by(Question.id).all()
      current_questions = paginate_questions(request, questions)

      if len(current_questions) == 0:
        abort(404)

      categories = Category.query.order_by(Category.id).all()
      if len (categories) == 0:
       abort(404)

      categories_list = []
      for category in categories:
        categories_list.append(category.type)

      return jsonify({
       'success': True,
       'questions': current_questions,
       'total_questions': len(questions),
       'current_category': categories_list,
       'categories': categories_list
      })



  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.get(question_id)
      if question is None:
        abort(404)

      question.delete()
      questions = Question.query.order_by(Question.id).all()
      current_questions = paginate_questions(request, questions)

      return jsonify({
        'success': True,
        'deleted': question_id,
        'questions': current_questions,
      })



  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def create_question():
    body = request.get_json()
    new_question = body.get('question')
    new_answer = body.get('answer')
    new_category = body.get('category')
    new_difficulty = body.get('difficulty')

    try:
      try:
      question = Question(question=new_question, answer=new_answer, difficulty=new_difficulty, category=new_category)
      question.insert()

      questions = Question.query.order_by(Question.id).all()
      current_questions = paginate_questions(request, questions)

      return jsonify({
        'success': True,
        'created': question.id,
        'questions': current_questions,
        'total_questions': len(questions)
      })

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods=['POST'])
  def search_questions():
    body = request.get_json()
    search_term = body.get('searchTerm', None)

    try:
      search_results = Question.query.filter(
        Question.question.ilike('%' + search_term + '%')).all()

      if search_results is None:
          abort(404)

      categories = Category.query.order_by(Category.id).all()

      if categories is None:
          abort(404)

      categories_list = []
      for category in categories:
          categories_list.append(
           category.type
          )

      return jsonify({
        'success': True,
        'total_questions': len(search_results),
        'questions': [question.format() for question in search_results],
        'current_category': categories_list
      })


  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions')
    def questoins_based_on_category(category_id):

        current_category = Category.query.get(category_id)
        current_questoins = Question.query.filter_by(
            category=category_id).all()
        print(current_questoins)

        if current_questoins is None:
            abort(404)

        found_questions = questions_pagination(
            request=request, selection=current_questoins)

        if len(found_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': found_questions,
            'total_questions': len(current_questoins),
            'current_category': category_id
        })


  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods = ['POST'])
  def play_quizz():

    body = request.get_json()

    previous_questions = body.get('previous_questions')
    quiz_category = body.get('quiz_category')

    if quiz_category is None:
      abort(422)

      question = Question.query.filter(
        Question.category == quiz_category.get('id')).filter(
        Question.id.notin_(previous_questions_list)).order_by(
        func.random()).limit(1).all()

      return jsonify({
        'success': True,
        'question': question
        })

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success': False,
      'error': 404,
      'message': "Resource Not Found"
      }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      'success': False,
      'error': 422,
      'message': "Unprocessable"
    }), 422

  
  
  return app

    