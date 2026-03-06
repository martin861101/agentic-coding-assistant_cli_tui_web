Act as a Senior Python Developer. Help me create a small project called 'Gold-ZAR Tracker.'
​Requirements:
​Use Python with the requests library.
​Fetch the current Gold price (per ounce) and the USD to ZAR exchange rate using a free API (like ExchangeRate-API or yfinance).
​Create a function that calculates the price of 1 gram of gold in ZAR.
Formula: (Gold Price / 31.1035) \times USDZAR Rate
​Display the results in a clean terminal table using the rich or tabulate library.
​Include basic error handling for the API requests."
​Why this is a good test for your assistant:
​API Logic: It tests if the assistant knows how to handle JSON responses and authentication headers.
​Mathematics: It checks if the assistant can correctly apply the conversion formula (Ounces to Grams).
​Formatting: It forces the assistant to think about the user interface (CLI tables).
