About this project
------------------
A simple online catalog, contains information about camping and hiking items.
You may add, edit and delete items in different categories, however, list of
categories are pre-configured and cannot be changed by easy way. To manipulate
with items, you must have GitHub account, application uses it to authorize you.

Prerequisites
-------------
[Follow the instructions](https://www.udacity.com/wiki/ud088/vagrant)
to install virtual machine (VM) on your computer. This VM gives you an environment
including a PostgreSQL and Python configured to run this project.
*Note: You need to install git on this VM. I have no idea why it missed.*

Installation
------------
- Log into VM and clone repository, and go to local directory
```bash
$ git clone https://github.com/nivanko/udacity-catalog.git
$ cd udacity-catalog
```
- Create database
```bash
$ createdb catalog
```
- Run setup script
```bash
$ python db.py
```
Setup script does not delete existing information. You may delete information
manually, if you want to run setup script again:
```bash
$ psql catalog -c "delete from item"
$ psql catalog -c "delete from category"
$ psql catalog -c "delete from users"
```

Usage
-----
Run application
```bash
$ python application.py
```
Open your favorite browser, and navigate to [http://localhost:8000/](http://localhost:8000/).
Application is tested with Google Chrome only. Setup script puts two sample items
into "Backpacks" category. In the **sample_data** directory, you may find
**catalog.csv** - semicolon-delimited list of items (it can be opened with any
spreadsheet program), and some image files. You must be logged in to add, edit
and delete items. You cannot manipulate items, created by other users.

---

***Disclaimer:*** All images, and some item's descriptions are taken from
[Wikipedia](http://wikipedia.org)
