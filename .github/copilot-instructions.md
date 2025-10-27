# Copilot Instructions for Population Prediction Model

## Project Overview

This is a population prediction model project (人口预测模型) designed to forecast:
- Population quantity (人口数量)
- Gender ratio (性别比例)
- Age structure (年龄结构)
- Related demographic changes

## Development Guidelines

### Code Quality Standards

- Write clean, maintainable, and well-documented code
- Follow PEP 8 style guidelines for Python code
- Use meaningful variable and function names
- Add docstrings to all functions, classes, and modules
- Include type hints where applicable

### Testing Requirements

- Write unit tests for all new functions and classes
- Aim for high test coverage (>80%)
- Use pytest as the testing framework
- Test edge cases and error conditions

### Documentation

- Update README.md when adding new features or changing functionality
- Document all model parameters and assumptions
- Include usage examples in documentation
- Add inline comments for complex algorithms

### Data Science Best Practices

- Use reproducible random seeds for consistency
- Document data sources and preprocessing steps
- Version control datasets when practical
- Validate model inputs and outputs
- Include visualization of results where appropriate

### Code Organization

- Keep models in a dedicated `models/` directory
- Store data processing utilities in `utils/` or `preprocessing/`
- Place tests in a `tests/` directory
- Configuration files should be in the root or `config/` directory

### Dependencies

- Use virtual environments (venv or conda)
- Maintain a `requirements.txt` or `environment.yml` file
- Pin major version numbers for stability
- Document any system-level dependencies

### Git Workflow

- Write clear, descriptive commit messages
- Keep commits focused and atomic
- Create feature branches for new work
- Reference issue numbers in commits when applicable

### Model Development

- Start with baseline models before complex ones
- Document model performance metrics
- Compare multiple approaches when solving problems
- Consider computational efficiency and scalability
- Validate models on held-out test data

### Common Patterns

- Use pandas for data manipulation
- Use numpy for numerical computations
- Use matplotlib/seaborn for visualizations
- Use scikit-learn for machine learning tasks
- Consider statsmodels for statistical modeling

## Language Support

This project supports both English and Chinese (中文). Comments and documentation can be in either language, though English is preferred for code and technical documentation to ensure broader accessibility.
