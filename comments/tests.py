from testing.testcases import TestCase


class CommentModelTests(TestCase):
    def setUp(self):
        self.jeeves = self.create_user('jeeves')
        self.honk = self.create_honk(self.jeeves)
        self.comment = self.create_comment(self.jeeves, self.honk)

    def test_comment(self):
        self.assertNotEqual(self.comment.__str__(), None)

    def test_like_set(self):
        self.create_like(self.jeeves, self.comment)
        self.assertEqual(self.comment.like_set.count(), 1)

        self.create_like(self.jeeves, self.comment)
        self.assertEqual(self.comment.like_set.count(), 1)

        brenda = self.create_user('brenda')
        self.create_like(brenda, self.comment)
        self.assertEqual(self.comment.like_set.count(), 2)
