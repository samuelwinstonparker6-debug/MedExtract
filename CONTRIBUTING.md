# Contributing to MedExtract

Thank you for your interest in contributing to **MedExtract**! We welcome pull requests, bug reports, and feature requests.

## How to Contribute

1. **Fork the Repository:** Create your own fork of the MedExtract repository.
2. **Clone the Repository:** Clone the forked repository to your local machine.
3. **Set up the Environment:** 
   - We highly recommend using Docker for a standardized development environment.
   - Run `docker-compose up --build` to start the backend and frontend.
4. **Create a Branch:** Create a feature or bugfix branch (`git checkout -b feature/your-feature-name`).
5. **Write Code:** Implement your changes. Ensure you adhere to standard Python PEP 8 styling for the backend and ESLint guidelines for the React frontend.
6. **Write Tests:** If you are adding a new feature, please add corresponding tests in the `tests/` directory. You can run the test suite using `pytest`.
7. **Submit a Pull Request:** Push your branch to your fork and submit a PR against the `main` branch of the upstream repository.

## Development Guidelines

- **Architecture:** Keep the extraction models modular. If you are adding a new document type, update `classifier.py` and `extractor.py` accordingly.
- **Performance:** Be mindful of the Machine Learning models used. We prefer lightweight base models over massive LLMs to keep background processing fast and resource-efficient.
- **Database:** If you change the SQLAlchemy models, generate and run Alembic migrations.

## Reporting Bugs

Please use the GitHub Issues tab to report bugs. Include:
- Steps to reproduce the bug.
- Expected versus actual behavior.
- Any relevant logs or stack traces.

Happy Coding!
