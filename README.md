<div align="center">

# ✨ Redshift Mate ✨

### A modern, web-based application for managing Amazon Redshift users, roles, and privileges

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/license/agpl-v3)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

![Redshift Mate Dashboard](placeholder-dashboard.gif)
*Placeholder for dashboard screencast*

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Contributing](#-contributing) • [License](#-license)

</div>

## 🌟 Why Redshift Mate?

Redshift Mate is designed as a companion tool for data engineering professionals working with Amazon Redshift data warehouses. Managing users, roles, and privileges through SQL commands or the AWS console can be tedious, error-prone, and often requires consulting documentation. Redshift Mate provides:

- **Intuitive Interface**: Easily manage complex permissions without writing SQL
- **Time Savings**: Accomplish in seconds what would take minutes or hours manually
- **Reduced Errors**: Visual confirmation of changes helps prevent security misconfigurations
- **Comprehensive View**: See all users, roles, and their relationships in one place
- **Documentation at Your Fingertips**: Complete tasks without constantly referring back to Redshift documentation

### 🎯 Target Audience

Redshift Mate is built for:
- **Data Engineers** managing Redshift clusters
- **Database Administrators** responsible for user access and security
- **DevOps Teams** handling infrastructure and permissions
- **Data Teams** needing simplified access management

## 🛠️ Technologies Used

- [FastHTML](https://github.com/python-fasthtml/fasthtml) - A Python library for building dynamic web interfaces with a declarative syntax
- [MonsterUI](https://github.com/monster-ui/monster-ui) - A modern UI component library for creating responsive web applications
- [Redshift Connector](https://github.com/aws/amazon-redshift-python-driver) - Official Amazon Redshift Python driver for database connectivity
- [Cryptography](https://cryptography.io/en/latest/) - Provides cryptographic recipes and primitives for secure data handling

## 🚀 Features

- **User Management**: Create, read, update, and delete Redshift database users
- **Role Management**: Create, read, update, and delete Redshift roles
- **Group Membership**: Assign users to groups and manage group memberships
- **Nested Roles**: Create role hierarchies by assigning roles to other roles
- **Fine-grained Privileges**: Manage access at schema, table, view, function, and procedure levels
- **Privilege Management**: Grant and revoke specific privileges (SELECT, INSERT, UPDATE, DELETE, EXECUTE)
- **Schema Explorer**: Browse database schemas and their objects
- **User-friendly Interface**: Built with FastHTML and MonsterUI for a responsive experience

## 📋 Requirements

- Python 3.8+
- Amazon Redshift cluster with superuser access
- Required Python packages:
  - python_fasthtml==0.12.4
  - redshift_connector==2.1.5
  - cryptography==44.0.2
  - MonsterUI>=1.0.0
  - requests>=2.28.0

## 🔧 Installation

### Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/redshift-mate.git
cd redshift-mate

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

## 🚦 Usage

Run the application with Python:

```bash
python app.py
```

Once the application is running:

1. Connect to your Redshift cluster by providing connection details in the web interface
2. Navigate through the intuitive UI to manage users, roles, and privileges
3. Changes are applied directly to your Redshift cluster

![Connection Screen](placeholder-connection.png)
*Placeholder for connection screen*

![User Management](placeholder-user-management.png)
*Placeholder for user management interface*

![Role Privileges](placeholder-role-privileges.png)
*Placeholder for role privileges configuration*

## 🔒 Security Notes

- The application requires superuser privileges to manage Redshift users and roles
- Connection details are encrypted in the session
- For production use, consider implementing additional security measures

## 📁 Project Structure

The project follows a modular architecture that separates UI components from database operations:

```
rs-mate/
├── app.py                  # Main application entry point
├── components/             # UI components and views
├── helpers/                # Helper functions and utilities
└── redshift/               # Redshift interaction layer
```

For a detailed breakdown of each module, see the [Architecture Documentation](CONTRIBUTING.md#project-structure).

## 📊 Screenshots

![Schema Explorer](placeholder-schema-explorer.png)
*Placeholder for schema explorer view*

![Privilege Management](placeholder-privilege-management.gif)
*Placeholder for privilege management workflow*

## 🔮 Future Development

This project is currently in MVP stage and will grow based on community feedback. As a companion for data engineering professionals, Redshift Mate aims to simplify both daily repetitive tasks and occasional complex operations that typically require consulting documentation.

Planned enhancements include:

### User & Security Management
- Enhanced monitoring and logging capabilities
- Batch operations for managing multiple users/roles
- Privilege templates and role-based access control patterns
- Audit trail for security compliance

### Data Engineering Workflow Improvements
- Query performance analysis and optimization suggestions
- Schema comparison and migration tools
- Automated vacuum and analyze operations
- Table statistics and storage optimization recommendations
- Data distribution key analysis

### Usability Enhancements
- Saved connection profiles
- Advanced search and filtering
- Command history and favorites
- Customizable dashboards for monitoring

We welcome contributions and feature requests from the data engineering community to help prioritize development efforts based on real-world needs.

## 🤝 Contributing

We welcome contributions to Redshift Mate! Whether you're fixing bugs, improving documentation, or adding new features, your help is appreciated.

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines on how to contribute to this project, including:

- Development setup
- Coding guidelines
- How to submit changes
- Using AI coding assistants with the provided context files
- Useful resources and documentation links

## 🙋 Support & Community

- **Issues**: Report bugs or request features on our [Issue Tracker](https://github.com/yourusername/redshift-mate/issues)
- **Discussions**: Join the conversation in our [GitHub Discussions](https://github.com/yourusername/redshift-mate/discussions)
- **Updates**: Follow [@YourTwitterHandle](https://twitter.com/yourtwitterhandle) for project announcements

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">
  <sub>Built with ❤️ by the Redshift Mate team</sub>
</div>
