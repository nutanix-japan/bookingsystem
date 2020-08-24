# Item Booking system

# How to delete current state
1. delete "db.sqlite3" file on app root directory. It is a DB data.
2. delete content of "*/migrations/" except \_\_init\_\_.py

# How to setup
1. Prepare Linux machine with python3 and pip3
2. Setup with script "initialize.sh". it will install django and create project.
3. Create super(root) user for the system as requested in the script

# How to start
Start with script "start.sh".
Caution, you should issue it on console or window manager(byobu/screen etc.).
If you issue the script through SSH directly, app will exit when you exit ssh session.
