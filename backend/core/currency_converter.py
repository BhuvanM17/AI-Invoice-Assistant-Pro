import os
import requests
from typing import Dict, Optional
import time
from datetime import datetime, timedelta


class CurrencyConverter:
    """
    Currency conversion service with caching to minimize API calls
    Supports both free and paid exchange rate APIs
    """

    def __init__(self):
        # For paid APIs like exchangeratesapi.io
        self.api_key = os.getenv("EXCHANGE_RATE_API_KEY")
        self.base_url = "https://api.exchangerate-api.com/v4/latest/"
        self.cache_duration = timedelta(minutes=30)  # Cache for 30 minutes
        self.cache = {}
        self.last_cache_update = {}

    def get_exchange_rate(self, from_currency: str, to_currency: str) -> float:
        """
        Get exchange rate from one currency to another

        Args:
            from_currency: Source currency code (e.g., 'USD')
            to_currency: Target currency code (e.g., 'EUR')

        Returns:
            Exchange rate as float

        Raises:
            ValueError: If currency codes are invalid
            RuntimeError: If API call fails
        """
        cache_key = f"{from_currency}_{to_currency}"

        # Check if we have a cached rate that's still valid
        if cache_key in self.cache:
            if datetime.now() - self.last_cache_update[cache_key] < self.cache_duration:
                return self.cache[cache_key]

        # Fetch new exchange rate
        rate = self._fetch_exchange_rate(from_currency, to_currency)

        # Update cache
        self.cache[cache_key] = rate
        self.last_cache_update[cache_key] = datetime.now()

        return rate

    def _fetch_exchange_rate(self, from_currency: str, to_currency: str) -> float:
        """
        Fetch exchange rate from API
        """
        # First, get rates with USD as base (or EUR if USD is not available)
        base_currency = "USD" if from_currency != "USD" else "EUR"

        try:
            # Get rates from base currency
            url = f"{self.base_url}{base_currency}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            if from_currency not in data['rates']:
                raise ValueError(
                    f"Source currency '{from_currency}' not supported")
            if to_currency not in data['rates']:
                raise ValueError(
                    f"Target currency '{to_currency}' not supported")

            # Calculate cross rate: from_currency -> base -> to_currency
            # How much of base currency equals 1 from_currency
            from_rate = data['rates'][from_currency]
            # How much of base currency equals 1 to_currency
            to_rate = data['rates'][to_currency]

            # Exchange rate: 1 from_currency = (1/from_rate) * to_rate of to_currency
            exchange_rate = to_rate / from_rate

            return exchange_rate

        except requests.exceptions.RequestException as e:
            print(f"Error fetching exchange rate: {e}")
            # Return a fallback rate or raise an exception
            raise RuntimeError(f"Failed to fetch exchange rate: {e}")
        except KeyError:
            raise ValueError(f"Invalid response format from exchange rate API")

    def convert_amount(self, amount: float, from_currency: str, to_currency: str) -> float:
        """
        Convert an amount from one currency to another

        Args:
            amount: Amount to convert
            from_currency: Source currency code
            to_currency: Target currency code

        Returns:
            Converted amount as float
        """
        if from_currency.upper() == to_currency.upper():
            return amount

        rate = self.get_exchange_rate(
            from_currency.upper(), to_currency.upper())
        return round(amount * rate, 2)

    def get_supported_currencies(self) -> list:
        """
        Get list of supported currencies
        """
        try:
            url = f"{self.base_url}USD"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return list(data['rates'].keys())
        except:
            # Return a default list if API call fails
            return ["USD", "EUR", "GBP", "JPY", "INR", "CAD", "AUD", "CHF", "CNY", "SEK", "NZD", "SGD"]


# Singleton instance
converter = CurrencyConverter()


def convert_currency(amount: float, from_currency: str, to_currency: str) -> float:
    """
    Convenience function to convert currency
    """
    return converter.convert_amount(amount, from_currency, to_currency)


def get_exchange_rate(from_currency: str, to_currency: str) -> float:
    """
    Convenience function to get exchange rate
    """
    return converter.get_exchange_rate(from_currency, to_currency)


if __name__ == "__main__":
    # Example usage
    try:
        # Convert 100 USD to EUR
        result = convert_currency(100, "USD", "EUR")
        print(f"100 USD = {result} EUR")

        # Convert 50 GBP to INR
        result = convert_currency(50, "GBP", "INR")
        print(f"50 GBP = {result} INR")

        # Get supported currencies
        currencies = converter.get_supported_currencies()
        print(f"Supported currencies: {len(currencies)} total")

    except Exception as e:
        print(f"Error: {e}")
