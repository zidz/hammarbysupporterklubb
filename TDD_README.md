# Hammarby Supporterklubb - TDD Test Suite

## 🎯 Overview

This test suite follows strict **Test-Driven Development (TDD)** methodology for the Hammarby Supporterklubb website. All tests are written in the **Red phase** - they will initially FAIL until the corresponding features are implemented.

## 📊 Test Coverage

- **Total Tests**: 100+ tests
- **Target Coverage**: 80%+
- **Test Files**: 6 comprehensive test modules

### Test Breakdown

| Test File | Tests | Coverage Area |
|-----------|-------|---------------|
| `conftest.py` | - | Shared fixtures and test data |
| `test_authentication.py` | 13 | Login, logout, session management, password security |
| `test_news_crud.py` | 15 | Create, read, update, delete news operations |
| `test_image_upload.py` | 18 | Upload validation, optimization, format support |
| `test_pages.py` | 27 | All 7 pages rendering and navigation |
| `test_quill_delta.py` | 27 | Quill Delta HTML rendering and security |

## 🏗️ Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── test_authentication.py   # Authentication tests
├── test_news_crud.py        # News CRUD operations
├── test_image_upload.py     # Image upload functionality
├── test_pages.py            # Page rendering tests
└── test_quill_delta.py      # Quill Delta rendering
```

## 🚀 Running Tests

### Prerequisites

```bash
# Install dependencies
pip install -r requirements.txt

# Verify pytest installation
pytest --version
```

### Run All Tests

```bash
# Run all tests with verbose output
pytest -v

# Run with coverage report
pytest --cov=backend --cov-report=html -v

# Run specific test file
pytest tests/test_authentication.py -v

# Run specific test class
pytest tests/test_pages.py::TestHomePage -v

# Run specific test function
pytest tests/test_authentication.py::TestLogin::test_login_with_valid_credentials -v
```

### Run Tests with Coverage

```bash
# Generate HTML coverage report
pytest --cov=backend --cov-report=html --cov-report=term-missing

# View coverage in terminal
pytest --cov=backend --cov-report=term-missing --cov-fail-under=80
```

## 🔴 TDD Workflow (Red-Green-Refactor)

### Phase 1: RED - Write Failing Tests ✅ COMPLETE

All tests are written and will initially FAIL. This is expected and correct.

```bash
# Verify tests fail (Red phase)
pytest -v
# Expected: Many failures - features not implemented yet
```

### Phase 2: GREEN - Implement Features

Implement features to make tests pass:

1. **Start with authentication** (`test_authentication.py`)
   ```bash
   # Run only authentication tests
   pytest tests/test_authentication.py -v
   ```
   
2. **Implement routes in `backend/routes/__init__.py`**
   - Login/logout endpoints
   - Session management
   - Password hashing

3. **Run tests again**
   ```bash
   pytest tests/test_authentication.py -v
   # Expected: Tests should pass
   ```

4. **Repeat for each test module**
   - News CRUD: `test_news_crud.py`
   - Image upload: `test_image_upload.py`
   - Pages: `test_pages.py`
   - Quill Delta: `test_quill_delta.py`

### Phase 3: REFACTOR - Improve Code

Once tests pass:

1. **Refactor implementation**
   - Improve code quality
   - Optimize performance
   - Add documentation

2. **Verify tests still pass**
   ```bash
   pytest -v
   # All tests should still pass
   ```

3. **Check coverage**
   ```bash
   pytest --cov=backend --cov-report=term-missing
   # Target: 80%+ coverage
   ```

## 📝 Test Fixtures

### Available Fixtures

| Fixture | Description | Scope |
|---------|-------------|-------|
| `app` | Test Flask application | function |
| `client` | Test client | function |
| `runner` | CLI test runner | function |
| `test_user` | Admin test user data | function |
| `test_user_regular` | Regular user data | function |
| `test_news_data` | Sample news articles | function |
| `test_image` | Test JPEG image | function |
| `test_image_png` | Test PNG image | function |
| `test_image_invalid` | Invalid file for testing | function |
| `quill_delta_sample` | Sample Quill Delta | function |
| `authenticated_client` | Authenticated test client | function |
| `admin_client` | Admin authenticated client | function |

### Using Fixtures

```python
def test_example(client, test_user):
    """Test using fixtures."""
    response = client.post('/login', data={
        'username': test_user['username'],
        'password': test_user['password']
    })
    assert response.status_code == 200
```

## 🧪 Test Categories

### Markers

Tests use pytest markers for categorization:

```bash
# Run only unit tests
pytest -m unit

# Run only authentication tests
pytest -m auth

# Run only admin tests
pytest -m admin
```

### Test Types

- **Unit Tests**: Test individual functions/methods
- **Integration Tests**: Test component interactions
- **Functional Tests**: Test complete user workflows

## 📋 Test Checklist

### Authentication (13 tests)
- [ ] Login with valid credentials
- [ ] Login with invalid credentials
- [ ] Login with missing username
- [ ] Login with missing password
- [ ] Login with nonexistent user
- [ ] Logout clears session
- [ ] Logout redirects to login
- [ ] Unauthenticated user cannot access admin
- [ ] Authenticated user can access admin
- [ ] Session persists across requests
- [ ] Session timeout
- [ ] Password not stored in session
- [ ] Password hashed in database

### News CRUD (15 tests)
- [ ] Create news as admin
- [ ] Create news requires title
- [ ] Create news requires content
- [ ] Create news unauthorized
- [ ] List all news
- [ ] View single news
- [ ] News pagination
- [ ] News by category
- [ ] News search
- [ ] Update news as admin
- [ ] Update news requires title
- [ ] Update news unauthorized
- [ ] Update nonexistent news
- [ ] Delete news as admin
- [ ] Delete news unauthorized
- [ ] Delete nonexistent news
- [ ] Delete news confirmation
- [ ] News title length limit
- [ ] News content length limit
- [ ] News invalid category

### Image Upload (18 tests)
- [ ] Upload valid JPEG
- [ ] Upload valid PNG
- [ ] Upload invalid file type
- [ ] Upload file size limit
- [ ] Upload no file
- [ ] Image resized to max dimensions
- [ ] Image quality preserved
- [ ] Image format converted to JPEG
- [ ] JPEG format supported
- [ ] PNG format supported
- [ ] GIF format supported
- [ ] WebP format supported
- [ ] BMP format not supported
- [ ] Image saved to upload folder
- [ ] Image filename sanitized
- [ ] Image unique filename generated
- [ ] Delete uploaded image
- [ ] Delete nonexistent image
- [ ] Delete image unauthorized

### Pages (27 tests)
- [ ] Home page loads
- [ ] Home page has navigation
- [ ] Home page has branding
- [ ] Home page has about section
- [ ] Home page has contact section
- [ ] News page loads
- [ ] News page displays list
- [ ] News page has pagination
- [ ] News page has search
- [ ] Board page loads
- [ ] Board page displays members
- [ ] Board page has contact
- [ ] Scholarship page loads
- [ ] Scholarship page displays criteria
- [ ] Scholarship page displays recipients
- [ ] Membership page loads
- [ ] Membership page displays benefits
- [ ] Membership page has join form
- [ ] Admin login page loads
- [ ] Admin login has username field
- [ ] Admin login has password field
- [ ] Admin login has submit button
- [ ] Admin dashboard requires auth
- [ ] Admin dashboard loads for auth user
- [ ] Admin dashboard displays news management
- [ ] Admin dashboard displays user management
- [ ] Admin dashboard displays settings
- [ ] Navigation links to home
- [ ] Navigation links to news
- [ ] Mobile menu works

### Quill Delta (27 tests)
- [ ] Simple text rendering
- [ ] Bold text rendering
- [ ] Header rendering
- [ ] List rendering
- [ ] Empty delta rendering
- [ ] Italic text rendering
- [ ] Bold and italic combined
- [ ] Color attribute rendering
- [ ] Link attribute rendering
- [ ] Link URL correct
- [ ] XSS script tag sanitized
- [ ] XSS event handler sanitized
- [ ] HTML entities encoded
- [ ] News content with Quill Delta
- [ ] News display renders Quill HTML
- [ ] Quill Delta in admin editor
- [ ] Very long text handling
- [ ] Special characters handling
- [ ] Newlines and paragraphs
- [ ] Mixed formatting

## 🐛 Debugging Tests

### Run Test in Isolation

```bash
# Run single test with full traceback
pytest tests/test_authentication.py::TestLogin::test_login_with_valid_credentials -v -s

# Run with pdb debugger
pytest tests/test_authentication.py::TestLogin::test_login_with_valid_credentials --pdb
```

### View Test Output

```bash
# Show print statements
pytest -v -s

# Show captured output
pytest -v --capture=no
```

### Failed Tests

```bash
# Run only previously failed tests
pytest --lf

# Run failed tests first
pytest --ff
```

## 📈 Coverage Reports

### Terminal Report

```bash
pytest --cov=backend --cov-report=term-missing
```

### HTML Report

```bash
pytest --cov=backend --cov-report=html
# Open htmlcov/index.html in browser
```

### XML Report (for CI/CD)

```bash
pytest --cov=backend --cov-report=xml:coverage.xml
```

## ✅ Success Criteria

- [ ] All 100+ tests pass
- [ ] Code coverage ≥ 80%
- [ ] No test warnings
- [ ] All features implemented
- [ ] Documentation complete

## 🔄 Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run tests with coverage
        run: |
          pytest --cov=backend --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## 📚 Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-flask Documentation](https://pytest-flask.readthedocs.io/)
- [TDD Methodology](https://en.wikipedia.org/wiki/Test-driven_development)
- [Flask Testing](https://flask.palletsprojects.com/en/3.0.x/testing/)

## 📞 Support

For issues or questions:
1. Check existing test failures
2. Review fixture definitions in `conftest.py`
3. Consult pytest documentation
4. Review implementation requirements

---

**Status**: ✅ RED Phase Complete - All tests written and failing as expected
**Next**: Implement features to turn tests GREEN
