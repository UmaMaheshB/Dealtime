# Dealtime
### By Uma Mahesh Bandi
This is one of the project for the Udacity [FSND Course](https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd004).

### Project Overview
This applications displays different categories with respective categorical items, Any user can view the item details but only authenticated people can add, edit, delete items. 


### Why This Project?
Modern web applications perform a variety of functions and provide amazing features and utilities to their users; but deep down, it’s really all just creating, reading, updating and deleting data. In this project, you’ll combine your knowledge of building dynamic websites with persistent data storage to create a web application that provides a compelling service to your users.

### What Will I Learn?
  * Develop a RESTful web application using the Python framework Flask.
  * Implementing Login mechanisam using third-party OAuth authentication.
  * Implementing CRUD (create, read, update and delete) operations on favourite database.

## Skills Required
1. Python
2. HTML
3. CSS
4. OAuth
5. Flask Framework
6. flask_sqlalchemy

#### Requirements
  * [Python](https://www.python.org/downloads)
  * [Vagrant](https://www.vagrantup.com/)
  * [VirtualBox](https://www.virtualbox.org/)
  * [Git](https://git-scm.com/downloads) - for windows
  
#### Project Setup:
  1. Install Vagrant 
  2. Install VirtualBox
  3. Download or Clone [fullstack-nanodegree-vm](https://github.com/udacity/fullstack-nanodegree-vm) repository.
  4. Unzip the above vagrant zip folder and open it
  5. Move the Dealtime folder into above vagrant folder
  
#### Running Project
  1. open git bash from vagrant folder
  2. Launch the Vagrant VM using command:
  `
    $ vagrant up
  `
  3. Log into Vagrant VM using command:
  `
    $ vagrant ssh
  `
  4. Move to server side vagrant folder using commmand:
  `
    $ cd /vagrant
  `
  5. Move to Project folder ie Dealtime using command:
  `
    $ cd Dealtime
  `
  6. Installing the required modules for our project using command:
  `
    $ ./requirements.sh
  `
  7. creating database structure using:
  `
  $ python db_create.py
 `
  8. intializing database with data using:
  `
  $ python db_init.py
 `
  9. Run the project using command:
  `
    $ python main.py
  `
  10. open our application by visiting from your favourite browser[http://localhost:5000](http://localhost:5000).
  ### JSON end points
  in this application we created json end points for multi purpose using REST architecture 
#### urls:
`
http://localhost:5000/items/JSON
`
`
http://localhost:5000/categories/JSON
`
`
http://localhost:5000/category/1/items/JSON
`
  