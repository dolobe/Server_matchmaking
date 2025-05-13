# Database Setup for Matchmaking Project

This README file provides instructions and information regarding the database setup for the Matchmaking Project.

## Database Overview

The Matchmaking Project uses a MySQL database to store various entities related to the matchmaking system. The following tables are defined in the database:

- **User**: Stores user information.
- **Role**: Defines different roles that users can have.
- **UserRole**: Associates users with their respective roles.
- **UserManager**: Manages user-related operations.
- **Game**: Represents the games available in the system.
- **Queue**: Manages the queue of players waiting for a match.
- **Log**: Records actions and events within the system.
- **Match**: Contains information about ongoing and completed matches.
- **Turn**: Records the turns taken in each match.
- **MatchConfig**: Stores configuration settings for matches.
- **Session**: Manages user sessions.
- **Statistic**: Records statistics related to matches and players.

## Database Setup Instructions

1. **Install MySQL**: Ensure that MySQL is installed on your machine. You can download it from the [official MySQL website](https://www.mysql.com/).

2. **Create Database**: Use the following SQL command to create a new database for the Matchmaking Project:
   ```sql
   CREATE DATABASE matchmaking_db;
   ```

3. **Run SQL Script**: Import the `db.sql` file located in the `database` directory to set up the necessary tables and relationships. You can do this using phpMyAdmin or by executing the following command in the MySQL command line:
   ```sql
   SOURCE path/to/matchmaking-project/database/db.sql;
   ```

4. **Configure Database Connection**: Update the database connection settings in the Django `settings.py` file located in `server/server/` to connect to your MySQL database. Ensure you have the necessary credentials (username, password, database name).

5. **Migrate Models**: After setting up the database, run the following command to apply any migrations:
   ```bash
   python manage.py migrate
   ```

## Additional Information

- Ensure that you have the necessary Python packages installed for MySQL support in Django. You can add `mysqlclient` to your `requirements.txt` file and install it using pip:
  ```bash
  pip install -r server/requirements.txt
  ```

- For any issues or questions regarding the database setup, please refer to the official Django documentation or MySQL documentation.

## Conclusion

This README provides a comprehensive guide to setting up the database for the Matchmaking Project. Follow the instructions carefully to ensure a successful setup.