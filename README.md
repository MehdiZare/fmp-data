## Environment Setup

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and add your API key:
```bash
FMP_API_KEY=your_api_key_here
```

3. For development, you can get a free API key from [FMP](https://financialmodelingprep.com/developer/docs/)

4. Never commit your `.env` file or API keys to the repository

## Running Tests

The test suite uses mocked responses and doesn't require an actual API key. To run tests:

```bash
poetry run pytest
```

For integration tests (optional):
```bash
FMP_TEST_API_KEY=your_test_api_key poetry run pytest tests/integration/
```
