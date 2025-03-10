expansion_prompt = """
Return 3 alternative search queries for the original query below.
FORMAT: Return ONLY a raw JSON object with exactly 3 queries. No explanation or other text.
EXAMPLE: {{"query1": "first query", "query2": "second query", "query3": "third query"}}

Original Query: {query}
"""