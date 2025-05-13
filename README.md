# Matchmaking Project

## Overview
This project is a matchmaking server for a turn-based Tic Tac Toe game. It consists of three main components: a server for matchmaking, a client application for players, and a MySQL database for data storage.

## Components

### Server
- **Framework**: Django
- **Functionality**: 
  - Handles matchmaking and game logic.
  - Manages player queues and matches.
  - Communicates with clients via WebSockets.
- **Directory**: `server/matchmaking/`
  - Contains models, views, serializers, and WebSocket handling.

### Client
- **Framework**: Python with Tkinter for GUI
- **Functionality**: 
  - Allows players to enter a queue, play the game, and receive updates.
  - Supports both GUI and command-line interfaces.
- **Directory**: `client/src/`
  - Contains the main application logic, GUI components, and socket communication.

### Database
- **Database Management**: MySQL
- **Functionality**: 
  - Stores user data, game statistics, and match history.
- **Directory**: `database/`
  - Contains SQL scripts for database setup and migrations.

## Installation
1. Clone the repository.
2. Navigate to the `server` directory and install the required packages:
   ```
   pip install -r requirements.txt
   ```
3. Set up the MySQL database using the provided `db.sql` script in the `database` directory.
4. Run the Django server:
   ```
   python manage.py runserver
   ```
5. For the client, navigate to the `client/src` directory and run:
   ```
   python main.py
   ```

## Usage
- Players can connect to the server and enter the matchmaking queue.
- Once matched, they can play Tic Tac Toe against each other.
- The game supports real-time updates and displays the current game state.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.