from django.test import TestCase
from users.models import Quote, DailyQuote
from datetime import date
from django.utils.timezone import now
from unittest.mock import patch

class QuoteModelTest(TestCase):
    """Test suite for the Quote model and its methods."""

    def setUp(self):
        self.quote1 = Quote.objects.create(text="The only limit to our realization of tomorrow is our doubts of today.")
        self.quote2 = Quote.objects.create(text="Success is not final, failure is not fatal.")
        self.quote3 = Quote.objects.create(text="What we think, we become.")

    def test_quote_str_representation(self):
        """Test the string representation of a Quote."""
        self.assertEqual(str(self.quote1), f'"{self.quote1.text}"')
        self.assertEqual(str(self.quote2), f'"{self.quote2.text}"')

    def test_get_quote_of_the_day_creates_daily_quote(self):
        """Test that get_quote_of_the_day() creates a new DailyQuote if none exists for today."""
        result = Quote.get_quote_of_the_day()
        
        daily_quote = DailyQuote.objects.filter(date=now().date()).first()
        
        self.assertIsNotNone(daily_quote)
        self.assertEqual(result, daily_quote.quote.text)
        self.assertIn(result, [self.quote1.text, self.quote2.text, self.quote3.text])

    def test_get_quote_of_the_day_returns_existing_quote(self):
        """Test that get_quote_of_the_day() returns the existing quote if already set for today."""
        daily_quote = DailyQuote.objects.create(date=now().date(), quote=self.quote1)
        
        result = Quote.get_quote_of_the_day()
        
        self.assertEqual(result, self.quote1.text)

    def test_get_quote_of_the_day_updates_with_new_quote(self):
        """Test that get_quote_of_the_day() updates DailyQuote with a new quote if it was None."""
        daily_quote = DailyQuote.objects.create(date=now().date(), quote=None)
        
        result = Quote.get_quote_of_the_day()
        
        updated_daily_quote = DailyQuote.objects.get(date=now().date())
        
        self.assertIsNotNone(updated_daily_quote.quote)
        self.assertEqual(result, updated_daily_quote.quote.text)

    def test_get_quote_of_the_day_no_quotes_available(self):
        """Test that get_quote_of_the_day() handles the case where no quotes are available."""
        Quote.objects.all().delete()

        with patch('users.models.Quote.ensure_default_quotes_exist') as mock_ensure_defaults:
            mock_ensure_defaults.return_value = None  # Prevent default quotes from being added
            
            result = Quote.get_quote_of_the_day()
            
            self.assertEqual(result, "No quote available today.")

