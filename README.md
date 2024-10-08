# Smart_Procurement_System_GPT

## Overview
Smart Procurement is a Flask-based application that manages procurement processes, leveraging a MySQL database for data storage.

## Requirements
Before you begin, ensure you have the following installed:
- Python 3.x
- MySQL Server

## Setting Up the Project
1. **Clone the Repository**: First, clone this repository to your local machine.
    ```bash
    git clone <repository-url>
    cd <repository-name>
    ```

2. **Create a Virtual Environment**: Create a virtual environment for the project. This will isolate your dependencies.
    ```bash
    python -m venv venv
    ```

3. **Activate the Virtual Environment**: Activate the virtual environment with the following command:
    - **On Windows**:
        ```bash
        .\venv\Scripts\activate
        ```
    - **On macOS/Linux**:
        ```bash
        source venv/bin/activate
        ```

4. **Install Dependencies**: Install the necessary packages using the `requirements.txt` file.
    ```bash
    pip install -r requirements.txt
    ```

5. **Set Environment Variables**: Set the environment variable for your Flask application:
    - **On Windows**:
        ```bash
        set FLASK_APP=app:init_app
        ```
    - **On macOS/Linux**:
        ```bash
        export FLASK_APP=app:init_app
        ```

6. **Upgrade Flask-WTF**: Upgrade the Flask-WTF package to the latest version.
    ```bash
    pip install --upgrade Flask-WTF
    ```

7. **Create the MySQL Database**: Log into your MySQL server and create the database:
    ```sql
    CREATE DATABASE tender_db;
    ```

8. **Initialize Database Migrations**: Copy the existing migration folder to a different location, if necessary, to keep a backup before you delete it.
    ```bash
    # Assuming you have a folder named migrations
    cp -r migrations ../backup_migrations  # Adjust path as necessary
    rm -r migrations
    flask db init
    ```

9. **Restore Migration Files**: Copy your migration files back to the new migrations folder you created in step 8.
    ```bash
    # Copy the migration files from backup
    cp -r ../backup_migrations/* migrations/
    ```

10. **Upgrade the Database**: Run the database upgrade command to apply the migrations.
    ```bash
    flask db upgrade
    ```

11. **Update SQLALCHEMY_DATABASE_URI**: In your `.env` or configuration file, replace the database URI with the following:
    ```plaintext
    SQLALCHEMY_DATABASE_URI=mysql+pymysql://root@localhost/tender_db
    ```

## Contributing
Contributions are welcome! Please feel free to submit a pull request.

## License
This project is licensed under the MIT License. See the LICENSE file for details.
