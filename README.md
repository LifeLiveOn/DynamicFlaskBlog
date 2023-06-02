Blog Website
This is a simple blog website built with Flask, SQLAlchemy, and Bootstrap. The website allows users to create, view, and interact with blog posts, including features like comments and likes. It also includes a search functionality and a user authentication system.

Features
User registration and login
Create, edit, and delete blog posts
Comment on blog posts
Like/unlike blog posts
Search for blog posts
Responsive design using Bootstrap
Installation
Clone the repository:

Create a virtual environment and activate it: cd blog-website python3 -m venv venv source venv/bin/activate

Install the required packages: pip install -r requirements.txt

Set up the environment variables:

Create a .env file in the project's root directory and add the following variables:

SECRET_KEY=<your_secret_key> SQLALCHEMY_DATABASE_URI=<your_database_uri> OWN_EMAIL=<your_email> OWN_PW=<your_email_password>

Make sure to replace <your_secret_key>, <your_database_uri>, <your_email>, and <your_email_password> with your own values.

Usage
Run the following command to start the application:

Open your web browser and navigate to http://localhost:5000 to access the blog website.

Contributing
Contributions are welcome! If you find any bugs or have suggestions for improvements, please submit an issue or a pull request.

License
This project is licensed under the MIT License.

Note
Important: Before running the application, make sure to create your own .env file with the required environment variables. This includes setting your own secret key, database URI, email account, and email password. Keep these values private and do not commit them to version control.
