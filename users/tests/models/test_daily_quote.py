from django.test import TestCase
from users.models import DailyQuote, Quote
from django.db import IntegrityError
from datetime import date

class DailyQuoteModelTest(TestCase):
    """Test suite for the DailyQuote model."""

    def setUp(self):
        self.quote1 = Quote.objects.create(text="Success is not final, failure is not fatal.")
        self.quote2 = Quote.objects.create(text="The only limit to our realization of tomorrow is our doubts of today.")

    def test_create_daily_quote(self):
        """Test creating a DailyQuote with a Quote"""
        daily_quote = DailyQuote.objects.create(date=date.today(), quote=self.quote1)
        self.assertEqual(daily_quote.quote, self.quote1)
        self.assertEqual(daily_quote.date, date.today())
        self.assertEqual(str(daily_quote), f"Daily Quote for {date.today()}: {self.quote1.text}")

    def test_date_field_uniqueness(self):
        """Test the uniqueness constraint on the date field"""
        DailyQuote.objects.create(date=date.today(), quote=self.quote1)

        with self.assertRaises(IntegrityError):
            DailyQuote.objects.create(date=date.today(), quote=self.quote2)

    def test_quote_deletion_cascade(self):
        """Test that deleting a Quote deletes the related DailyQuote"""
        daily_quote = DailyQuote.objects.create(date=date.today(), quote=self.quote1)
        self.assertTrue(DailyQuote.objects.filter(id=daily_quote.id).exists())

        self.quote1.delete()
        
        self.assertFalse(DailyQuote.objects.filter(id=daily_quote.id).exists())

    def test_daily_quote_without_quote(self):
        """Test creating a DailyQuote without a Quote (quote is null)"""
        daily_quote = DailyQuote.objects.create(date=date.today(), quote=None)
        self.assertIsNone(daily_quote.quote)
        self.assertEqual(str(daily_quote), f"Daily Quote for {date.today()}: None")
