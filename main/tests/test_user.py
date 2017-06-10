from django.test import TestCase
from main.models import User

import util.ctrl
import util.user

class UserTestCase(TestCase):
    def setUp(self):
        User.objects.create(
            username = 'tester',
            nickname = '测试员',
            question = 'question1',
            answer1 = util.ctrl.salty('password1'),
            answer2 = util.ctrl.salty('password2'),
            tip = '',
            email = 'test@kyan001.com',
            headimg = ''
        )

    def test_check_answer(self):
        user = User.objects.get(username='tester')
        self.assertTrue(util.user.checkAnswer(user, 'password1'))
        self.assertTrue(util.user.checkAnswer(user, 'password2'))
        self.assertFalse(util.user.checkAnswer(user, 'password3'))
