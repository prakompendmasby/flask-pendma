from flask_bootstrap import Bootstrap
from flask import Flask, render_template, flash, request, redirect, url_for


def create_app():
  app = Flask(__name__)
  Bootstrap(app)
  return app


app = create_app()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def elements():
    return render_template('about.html')



if __name__ == '__main__':
    app.run()
