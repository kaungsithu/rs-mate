<div align="center">

# ✨ <span style="color:#7c3aed">Redshift Mate</span> ✨

### A modern, web-based application for managing Amazon Redshift users, roles, and privileges

[![License: MIT](https://img.shields.io/badge/License-AGPL-blue.svg)](https://opensource.org/license/agpl-v3)
[![Python 3.8+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

![RSMate Screencast](./img/rsmate_screen_record_um.gif)

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Contributing](#-contributing) • [License](#-license)

</div>

## 🌟 Why RSMate?

Managing database users and their privileges on [Amazon Redshift](https://aws.amazon.com/redshift/) is not that easy -- at least it is for me. Thus, I decided to make a UI for that and I'm sure it will be useful for fellow *data engineers* out there using Amazon Redshift.  

Honestly, RSMate is a by-product of me tryig to learn [FastHTML](https://fastht.ml) and trying to force myself to read Amazon Redshift documentations for system tables 😄.  

I'm hoping RSMate to be a companion tool for *data engineers* working with Amazon Redshift. It currently has basic users, roles, groups and privileges management functionalities. Over the time, I will be adding more complete privileges management functionality and other helpful features dealing with Amazon Redshift -- for instance, UI for tracing hierarchical dependencies of a relation. So, stay tuned!, my fellow *data engineering* folks! and click on the **star** and **watch** buttons to stay up to date and to let me know there are users RSMate is helping in a way. That will give me motivations and energy to keep coding ⚡️.


## 🚀 Features  

- **User**: View, create, update, and delete Redshift database users
- **Role**: View, create, update, and delete Redshift roles
- **Nested Roles**: Create role hierarchies by assigning roles to other roles
- **Group**: Assign users to groups _(So far, I found groups only useful in **WLM**)_
- **Fine-grained Privileges**: Manage access at schema, table, view, function, and procedure levels
- **Privilege Management**: Grant and revoke specific privileges (SELECT, INSERT, UPDATE, DELETE, EXECUTE)


## ⚙️ Installation

### Quick Start

```bash
# Clone the repository
git clone https://github.com/kaungsithu/rs-mate.git
cd rs-mate

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

> It is always a good idea to run the application in a virtual environment.  

```bash
python -m venv venv
source venv/bin/activate
```

## 🚦 Usage

Once the application is running:

1. Go to `http://localhost:5001` in your browser
2. Connect to your Redshift cluster by providing connection details in the web interface
  - The app is sort of a database client, as long as your network is accessible to Redshift, it should get connected.
3. Changes are applied directly to your Redshift cluster by running SQL commands

![Connection Screen](/img/connection-screen.png)

## 🔒 Security Notes

- The application requires superuser privileges to manage Redshift users and roles
- Connection details are encrypted in the session
- For production use, consider implementing additional security measures like hosting in the same **VPC** as your Redshift cluster and enabling **SSL**.

## 🛠️ Technologies Used

- [FastHTML](https://github.com/python-fasthtml/fasthtml) - A Python library for building dynamic web interfaces with a declarative syntax
- [MonsterUI](https://github.com/monster-ui/monster-ui) - A modern UI component library for creating responsive web applications
- [Redshift Connector](https://github.com/aws/amazon-redshift-python-driver) - Official Amazon Redshift Python driver for database connectivity
- [Cryptography](https://cryptography.io/en/latest/) - Provides cryptographic recipes and primitives for secure data handling


## 🔮 Future Development

This project is currently in MVP stage and will grow based on community feedback. *Please feel free to report issues, contribute to help make RSMate better for all of us!*

I currently have these in mind for future development:
- More complete user and role management functionalities
  - e.g. password reset, default privileges, user and role summaries etc.
- Better UX for privilege management
  - e.g. grant/revoke whole schema, all tables (select/unselect all...)
- Graphical views of privilege hierarchies
- Database relation dependencies visualization
- And more...

## 🤝 Contributing

Contributions are welcome! Whether you're fixing bugs, improving documentation, or adding new features, your help is appreciated.

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines on how to contribute to this project, including:

## 📄 License

This project is licensed under the AGPL-3.0 License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">
  <sub>Built with ❤️</sub>
</div>
