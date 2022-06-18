import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category

from dotenv import load_dotenv
load_dotenv()


test_database_name = os.getenv('TEST_DATABASE_NAME')
database_path = f'postgres://{os.getenv("DATABASE_USERNAME")}:{os.getenv("DATABASE_PASSWORD")}@localhost:5432/{test_database_name}'


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = test_database_name
        self.database_path = database_path
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_1_get_categories(self): # get all categories
        res = self.client().get('/categories')
        date = json.loads(res.data)

        self.assertEquals(res.status_code, 200)
        self.assertTrue(date['success'])
        self.assertTrue(len(date['categories']))

    # def test_2_get_categories_not_found(self):
    #     res = self.client().get('/categories/1000')
    #     data = json.loads(res.data)

    #     self.assertEqual(res.status_code, 404)
    #     self.assertFalse(data['success'])
    #     self.assertEqual(data['message'], 'resource not found')

    def test_3_get_questions(self): # get all questions
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEquals(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['categories']))

    def test_4_get_questions_by_category(self): # get questions by category
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEquals(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['categories']))

    def test_5_get_questions_by_category_not_found(self): 
        res = self.client().get('/categories/1000/questions')
        data = json.loads(res.data)
    
        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'resource not found')

    def test_6_delete_question(self): # delete question
        res = self.client().delete('/questions/4')
        data = json.loads(res.data)

        question = Question.query.filter(Question.id==10).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['deleted'], 4)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertEqual(question, None)

    def test_12_delete_question_not_found(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEquals(res.status_code, 422)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'unprocessable')


    def test_7_create_question(self): # create question
        res = self.client().post('/questions', json={
            'question': 'What is the best food?',
            'answer': 'Pizza',
            'category': 1,
            'difficulty': 1
        })
        data = json.loads(res.data)

        self.assertEquals(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['created'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    # def test_8_create_invalid_question(self):
    #     res = self.client().post('/questions/45')
    #     data = json.loads(res.data)

    #     self.assertEquals(res.status_code, 422)
    #     self.assertFalse(data['success'])
    #     self.assertEqual(data['message'], 'unprocessable')
        

    def test_9_search_questions(self): # search questions
        res = self.client().post('/questions/search', json={
            'searchTerm': 'What'
        })
        data = json.loads(res.data)

        self.assertEquals(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['categories']))

    def test_10_search_questions_not_found(self):
        res = self.client().post('/questions/search/9')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'resource not found')

    def test_11_get_quiz_questions(self): # get quiz questions
        res = self.client().post('/quizzes', json={
            'quiz_category': {'id': 0, 'type': 'click'},
            'previous_questions': []
        })
        data = json.loads(res.data)

        self.assertEquals(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['question']))



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()