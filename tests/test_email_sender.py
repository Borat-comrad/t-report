import unittest

from email_sender import EmailSendError, parse_recipients


class EmailSenderTests(unittest.TestCase):
    def test_parse_recipients_accepts_comma_semicolon_and_newline(self) -> None:
        recipients = parse_recipients(
            "first@example.com, second@example.com; third@example.com\nfourth@example.com"
        )

        self.assertEqual(
            recipients,
            (
                "first@example.com",
                "second@example.com",
                "third@example.com",
                "fourth@example.com",
            ),
        )

    def test_parse_recipients_rejects_empty_value(self) -> None:
        with self.assertRaises(EmailSendError):
            parse_recipients(" , ; \n ")


if __name__ == "__main__":
    unittest.main()
