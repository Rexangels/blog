# Project Structure

This document outlines the directory structure of the blog project, providing a brief explanation of the purpose and contents of each key file and folder.

*   `manage.py`: Django's command-line utility for administrative tasks such as running the development server, creating database migrations, and interacting with the database.

*   `ai_blog/`: The main project directory. This directory contains project-level settings and configurations.
    *   `settings.py`: Project settings and configurations, including database settings, installed applications, middleware, authentication, and other global settings.
    *   `urls.py`: The main URL routing configuration for the entire project. It maps URLs to different applications and views.
    *   `wsgi.py`: The entry point for WSGI (Web Server Gateway Interface) servers, allowing the Django application to be served by web servers like Apache or Nginx.
    *   `asgi.py`: The entry point for ASGI (Asynchronous Server Gateway Interface) servers, used for asynchronous web applications.
    *   `__init__.py`:  An empty file that tells Python that this directory should be considered a Python package.

*   `blog/`: The blog application directory. This is a self-contained Django application responsible for managing blog-related functionality.
    *   `models.py`: Defines the database models for the blog application, such as `Post`, `Category`, `Tag`, `Comment`, etc. These models represent the structure of the data stored in the database.
    *   `views.py`: Contains the views that handle HTTP requests and responses for the blog application. Views process user input, interact with models, and render templates to display data.
    *   `urls.py`: Defines the URL routing configuration for the blog application, mapping URLs to specific views within the application.
    *   `forms.py`: Contains Django forms used for creating, editing, and validating blog posts, comments, and other data submitted by users.
    *   `templates/`: This directory stores the HTML templates used to render blog pages, such as the post list, post detail, category detail, and other views.  Templates use Django's template language to dynamically display data from the views.
        *   `blog/`:  A subdirectory (best practice) containing the actual template files for the blog app (e.g., `post_list.html`, `post_detail.html`, `post_form.html`).
    *   `static/`: Contains static files such as CSS stylesheets, JavaScript files, images, and other assets used to style and enhance the blog's user interface.
        *   `blog/`:  A subdirectory (best practice) containing static files specific to the blog app.
    *   `migrations/`: Stores database migration files.  Migrations track changes to the models and allow the database schema to be updated accordingly.
        *   `__init__.py`:  An empty file to indicate a Python package.
        *   `0001_initial.py`, `0002_...py`, etc.: Migration files representing changes to the database schema over time.
    *   `admin.py`:  Registers the blog models with the Django admin interface, allowing administrators to manage blog content through a web-based interface.
    *   `apps.py`: Contains the application configuration for the blog app.
    *   `tests.py`:  Contains unit tests for the blog application to ensure its functionality works as expected.
    *   `__init__.py`:  An empty file to indicate a Python package.

*   `accounts/`:  The accounts application directory. This is another self-contained Django application, responsible for user authentication, registration, profiles, and related functionality. It typically has a structure similar to the `blog/` application, with `models.py`, `views.py`, `urls.py`, `forms.py`, `templates/`, `migrations/`, etc.

*   `media/`:  This directory stores uploaded media files, such as user profile pictures or featured images for blog posts.  Django needs to be configured to serve files from this directory.
    *   `profile_pics/`: (Example) A subdirectory to store user profile pictures.

*   `doc/`: Contains documentation files for the project, providing information about its features, structure, development, and other relevant aspects.  This is where this `structure.md` file and other documentation reside.

*   `requirements.txt`: Lists the Python packages (dependencies) required to run the project. This file is used with `pip` to install the necessary packages.

*   `db.sqlite3`: The default SQLite database file used by Django during development.  In production, a more robust database system (like PostgreSQL or MySQL) would typically be used.