# Contributing to RSMate

> *Please note that this is a mostly AI generated document.*

Thank you for your interest in contributing to RSMate! This document provides guidelines and instructions to help you get started.

RSMate is designed as a companion tool for data engineering professionals working with Amazon Redshift data warehouses. Our goal is to simplify both daily repetitive tasks and occasional complex operations that typically require consulting documentation.

## Table of Contents

- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Coding Guidelines](#coding-guidelines)
- [Submitting Changes](#submitting-changes)
- [Using AI Coding Assistants](#using-ai-coding-assistants)
- [Useful Resources](#useful-resources)

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/redshift-mate.git
   cd redshift-mate
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   
   This will install all required packages:
   - python_fasthtml==0.12.4
   - redshift_connector==2.1.5
   - cryptography==44.0.2
   - MonsterUI>=1.0.0
   - requests>=2.28.0

4. Run the application:
   ```bash
   python app.py
   ```

## Project Structure

The project follows a modular structure:

```
rs-mate/
├── app.py                  # Main application entry point
├── requirements.txt        # Python dependencies
├── components/             # UI components
│   ├── __init__.py
│   ├── common.py           # Common UI elements
│   ├── database.py         # Database connection UI
│   ├── role.py             # Role management UI
│   └── user.py             # User management UI
├── helpers/                # Helper functions
│   ├── __init__.py
│   └── session_helper.py   # Session management helpers
└── redshift/               # Redshift interaction layer
    ├── __init__.py
    ├── database.py         # Database connection handling
    ├── privilege.py        # Privilege management
    ├── role.py             # Role operations
    ├── sql_queries.py      # SQL query definitions
    └── user.py             # User operations
```

## Coding Guidelines

- Use meaningful variable and function names
- Write docstrings for functions and classes
- Add comments for complex logic
- Keep functions small and focused on a single task

## Submitting Changes

1. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit them with a descriptive message:
   ```bash
   git commit -m "Add feature: description of your changes"
   ```

3. Push your branch to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

4. Create a pull request against the main repository

## Using AI Coding Assistants

This project includes context files for AI coding assistants in the `llms-ctx` directory. These files help large language models (LLMs) understand the libraries and frameworks used in the project. These files are downloaded from [FastHTML Docs](https://fastht.ml/docs/#getting-help-from-ai) and [MonsterUI](https://monsterui.answer.ai/). As these frameworks are relatively new to the GenAI Models as of now, these LLMS context files are very handy for AI Coding Assistants.

### What are the llms-ctx files?

The `llms-ctx` directory contains context files that provide information about:

- **FastHTML**: A Python library for building dynamic web interfaces with a declarative syntax
- **MonsterUI**: A modern UI component library for creating responsive web applications

These context files include API documentation, examples, and other information that helps AI coding assistants generate more accurate and relevant code suggestions.

### How to use them

When working with AI coding assistants like GitHub Copilot, Claude, or ChatGPT:

1. You can reference these files to help the AI understand the project structure and codes
2. Include relevant parts of these files in your prompts when asking for code suggestions
3. Use them as a reference when reviewing AI-generated code

## Useful Resources

### Documentation

- [FastHTML Documentation](https://fastht.ml/docs/)
- [MonsterUI Documentation](https://monsterui.answer.ai/)
- [Redshift Connector Documentation](https://github.com/aws/amazon-redshift-python-driver)

### Redshift & Data Engineering Resources

- [Amazon Redshift Documentation](https://docs.aws.amazon.com/redshift/index.html)
- [Redshift SQL Reference](https://docs.aws.amazon.com/redshift/latest/dg/cm_chap_SQLCommandRef.html)
- [Redshift Database Developer Guide](https://docs.aws.amazon.com/redshift/latest/dg/welcome.html)
- [Redshift Best Practices](https://docs.aws.amazon.com/redshift/latest/dg/best-practices.html)
- [Redshift Data API Reference](https://docs.aws.amazon.com/redshift-data/latest/APIReference/Welcome.html)

### UI Development Resources

- [FastHTML Quick Start](https://docs.fastht.ml/tutorials/quickstart_for_web_devs.html)

### Community

- [GitHub Issues](https://github.com/kaungsithu/rs-mate/issues)

## Feature Development Guidelines

When developing new features for RSMate, consider the following:

1. **User Experience**: Features should simplify complex Redshift operations and reduce the need to consult documentation
2. **Data Engineering Focus**: Prioritize features that help data engineers with their daily workflows
3. **Performance**: Ensure operations are efficient, especially when dealing with large Redshift clusters
4. **Security**: Follow best practices for handling credentials and sensitive information
5. **Documentation**: Include clear comments for any new features, or best, documentations.

### Potential Feature Areas

If you're looking for areas to contribute, consider these categories:

- **User & Security Management**: Improving the existing user, role, and privilege management
- **Data Engineering Workflows**: Adding tools for query optimization, schema management, etc.
- **Monitoring & Performance**: Features to help monitor and optimize Redshift performance
- **Usability Enhancements**: Improving the UI/UX 
- **TODOs**: There are TODO: comments in the code. They can easily be found with a VSCode extenstion like [TODO Tree](https://marketplace.visualstudio.com/items?itemName=Gruntfuggly.todo-tree)

## License

By contributing to RSMate, you agree that your contributions will be licensed under the project's AGPL-3.0 License.
