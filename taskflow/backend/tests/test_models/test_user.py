"""Module that contains the User class unittests."""

import unittest
from backend import create_app, db
from backend.models.user import User
from backend.utils.datetime_utils import ensure_datetime_fields


class TestUserClass(unittest.TestCase):
    """Unit tests for the User model."""
    def setUp(self):
        """Sets up the Flask app and database for all tests."""
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()
        self.user = User(
            id="f47ac10b-58cc-4372-a567-0e02b2c3d479",
            created_at="2025-05-01 22:00:00",
            updated_at="2025-05-02 18:12:00",
            name="testuser",
            email="testemail@example.com",
        )
        self.user.password = "123456"

    def tearDown(self):
        """Tears down the Flask app and database after the tests."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_id(self):
        """Tests that the user's id is correct."""
        self.assertIsInstance(self.user.id, str)
        self.assertEqual(self.user.id, "f47ac10b-58cc-4372-a567-0e02b2c3d479")

    def test_created_at(self):
        """Tests the user's created_at if it's correct."""
        self.assertIsInstance(self.user.created_at, str)
        self.assertEqual(self.user.created_at, "2025-05-01 22:00:00")

    def test_updated_at(self):
        """Tests the user's updated_at if it's correct."""
        self.assertIsInstance(self.user.updated_at, str)
        self.assertEqual(self.user.updated_at, "2025-05-02 18:12:00")

    def test_valid_name(self):
        """Tests that a valid name passes validation."""
        self.assertIsInstance(self.user.name, str)
        self.assertEqual(self.user.name, "testuser")

    def test_name_if_too_long(self):
        """Tests that setting the user's name too long raises a ValueError."""
        with self.assertRaises(ValueError) as context:
            self.user.name = "a" * 31
        self.assertIn("name must be between 3 and 30 characters",
                      str(context.exception))

    def test_name_if_too_short(self):
        """Tests that setting the user's name too short
        raises a ValueError."""
        with self.assertRaises(ValueError) as context:
            self.user.name = "aa"
        self.assertIn("name must be between 3 and 30 characters",
                      str(context.exception))

    def test_valid_email(self):
        """Tests that a valid email passes validation."""
        try:
            self.user.email = "valid.email@example.com"
        except ValueError:
            self.fail("Valid email raised ValueError unexpectedly.")

    def test_unique_email(self):
        """
        Verifies that cloning a user with a unique email
        successfully creates and saves a new user.
        """
        ensure_datetime_fields(self.user)
        self.user.save()
        user_2 = self.user.clone(email="unique@example.com", password="123456")
        self.assertIsNotNone(user_2.id)
        self.assertIsNotNone(user_2)
        self.assertEqual(user_2.email, "unique@example.com")

    def test_not_unique_email(self):
        """
        Verifies that cloning a user with a duplicate email
        raises an ValueError upon saving.
        """
        ensure_datetime_fields(self.user)
        self.user.save()
        with self.assertRaises(ValueError) as context:
            _ = self.user.clone(password="newpassword", email=self.user.email)
            self.assertIn(
                f"'email' value '{self.user.email}' already exists. "
                f"Must provide a unique value.",
                str(context.exception)
            )

    def test_email_must_have_exactly_one_at_symbol(self):
        """Tests that setting an email without exactly one '@'
        character raises a ValueError."""
        with self.assertRaises(ValueError) as context:
            self.user.email = "aa"
        self.assertIn("email must contain exactly one '@' character.",
                      str(context.exception))

    def test_email_cannot_start_or_end_with_at(self):
        """Tests that setting an email starting or ending with '@'
        raises a ValueError."""
        with self.assertRaises(ValueError) as context:
            self.user.email = "@"
        self.assertIn("email cannot start or end with '@'.",
                      str(context.exception))

    def test_email_cannot_start_or_end_with_dot(self):
        """Tests that setting an email starting or ending with '.'
        raises a ValueError."""
        with self.assertRaises(ValueError) as context:
            self.user.email = "a@."
        self.assertIn("email cannot start or end with '.'.",
                      str(context.exception))

    def test_email_cannot_contain_consecutive_dots(self):
        """Tests that setting an email containing consecutive dots ('..')
        raises a ValueError."""
        with self.assertRaises(ValueError) as context:
            self.user.email = "a@..com"
        self.assertIn("email cannot contain consecutive dots ('..').",
                      str(context.exception))

    def test_email_must_have_dot_after_at(self):
        """Tests that setting an email lacking a dot ('.') after the '@'
        raises a ValueError."""
        with self.assertRaises(ValueError) as context:
            self.user.email = "a.a@com"
        self.assertIn("email must contain a dot ('.') after the '@'.",
                      str(context.exception))

    def test_password_hashing_and_validation(self):
        """Tests that the user's password is hashed
        and validated correctly."""
        self.assertTrue(self.user.check_password("123456"))
        self.assertFalse(self.user.check_password("wrongpassword"))
        self.assertNotEqual(self.user._password, "123456")

    def test_password_getter_raises_error(self):
        """Tests that accessing raw password raises AttributeError."""
        with self.assertRaises(AttributeError):
            _ = self.user.password

    def test_save_method(self):
        """Tests that the save method adds and commits
        the user instance to the database."""
        ensure_datetime_fields(self.user)
        self.user.save()
        retrived = db.session.get(User, self.user.id)
        self.assertIsNotNone(retrived)
        self.assertEqual(retrived.name, self.user.name)
        self.assertEqual(retrived.email, self.user.email)

    def test_delete_method(self):
        """Tests that the delete method removes
        the user instance from the database."""
        ensure_datetime_fields(self.user)
        self.user.save()
        self.user.delete()
        retrived = db.session.get(User, self.user.id)
        self.assertIsNone(retrived)

    def test_to_dict_method(self):
        """Tests that the to_dict method returns a dict
        with object attributes."""
        expected_dict = {
            "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
            "created_at": "2025-05-01 22:00:00",
            "updated_at": "2025-05-02 18:12:00",
            "name": "testuser",
            "email": "testemail@example.com",
        }
        self.assertEqual(self.user.to_dict(), expected_dict)
        self.assertNotIn("_password", self.user.to_dict())

    def test_str_method(self):
        """Tests that the __str__ method returns a
        string representation of the object."""
        dict_rep = self.user.to_dict()
        expected_str = f"[User] ({self.user.id}) {dict_rep}"
        self.assertEqual(self.user.__str__(), expected_str)

    def test_clone_method(self):
        """Tests the the clone method."""
        user_2 = self.user.clone(email="unique@example.com", password="123456")
        self.assertNotEqual(user_2.id, self.user.id)
        self.assertNotEqual(user_2.created_at, self.user.created_at)
        self.assertNotEqual(user_2.updated_at, self.user.updated_at)
        self.assertNotEqual(user_2.email, self.user.email)

        self.assertEqual(user_2.name, self.user.name)


if __name__ == "__main__":
    unittest.main()
