## SI 364 - Winter 2018
## MIDTERM

####################
## Import statements
####################

from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, ValidationError
from wtforms.validators import Required, Length
from flask_sqlalchemy import SQLAlchemy
import tmdbsimple as tmdb
import datetime

############################
# Application configurations
############################
app = Flask(__name__)

app.config['SECRET_KEY'] = 'hard to guess string from si364'
## TODO 364: Create a database in postgresql in the code line below, and fill in your app's database URI. It should be of the format: postgresql://localhost/YOUR_DATABASE_NAME

## Your final Postgres database should be your uniqname, plus HW3, e.g. "jczettaHW3" or "maupandeHW3"
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://localhost/nisakhanmidterm"
## Provided:
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
tmdb.API_KEY = 'c91e04b96d4fdc9e8879a1c5606be639'



##################
### App setup ####
##################
# manager = Manager(app)
db = SQLAlchemy(app) # For database use

#########################
#########################
######### Everything above this line is important/useful setup,
## not problem-solving.##
#########################
#########################

#########################
##### Set up Models #####
#########################


class Movie (db.Model):
    __tablename__= "movies"
    movieId = db.Column (db.Integer, primary_key=True)
    movieText = db.Column (db.String (280))
    user_id = db.Column (db.Integer, db.ForeignKey("users.userId"))
    def __repr__(self):
        return "{} (ID: {})".format(self.movieText, self.movieId)


class User (db.Model):
    __tablename__= "users"
    userId = db.Column (db.Integer, primary_key=True)
    userUsername = db.Column (db.String (64), unique= True)
    userDisplay_name = db.Column (db.String (124))
    usermovie_relationship = db.relationship ("Movie", backref = "User")
    def __repr__(self):
        return "{} | ID: {}".format(self.userUsername, self.userId)

########################
##### Set up Forms #####
########################


class UserMovieForm(FlaskForm):
    text=StringField ("Enter movie title:", validators=[Required()])
    rating=StringField ("Enter your rating:", validators=[Required()])
    display_name=StringField ("Enter your display name:", validators=[Required()])
    submit=SubmitField ("Submit")

    def validate_display_name(self, field):
        display_here = field.data
        if len(display_here.split(" ")) < 2:
            raise ValidationError ("Display name must be at least 2 words")

    def validate_rating(self,field):
        rating_here = field.data
        if rating_here[-1] == "%":
            raise ValidationError ("!!!! ERRORS IN FORM SUBMISSION - [['Ratings ends with % sign -- leave off the % for rating!']]")
        if int(rating_here) < 0 or int(rating_here) > 100:
            raise ValidationError ("!!!! ERRORS IN FORM SUBMISSION - [['Ratings is out of range-- stay within 0-100.']]")
        if rating_here[0] == "-":
            raise ValidationError ("!!!! ERRORS IN FORM SUBMISSION - [['Ratings is out of range-- stay within 0-100.']]")

# class dateTimeMan(FlaskForm):
#     datedate = StringField('When did you watch this movie?', [Required()], format='%m/%d/%Y')

###################################
##### Routes & view functions #####
###################################

## Error handling routes - PROVIDED
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

#############
## Main route
#############

@app.route('/', methods=['GET', 'POST'])
def index():
    form = UserMovieForm()
    # form2 = dateTimeMan()
    num_movies=len(Movie.query.all())
    if form.validate_on_submit():
        rating=form.rating.data
        text=form.text.data
        display_name=form.display_name.data

        user1 = User.query.filter_by(userUsername=rating).first()
        if not user1:
            user1=User(userUsername=rating, userDisplay_name=display_name)
            db.session.add(user1)
            db.session.commit()

        movie_checker = Movie.query.filter_by(movieText=text,user_id=user1.userId).first()
        if movie_checker:
            flash("Movie exists")
            return redirect(url_for("see_all_movies"))
        else:
            tuserid=Movie(movieText=text, user_id=user1.userId)
            db.session.add(tuserid)
            db.session.commit()
            flash ("Movie is successfully added")
            return redirect(url_for("index"))

    errors = [v for v in form.errors.values()]
    if len(errors) > 0:
        flash("!!!! ERRORS IN FORM SUBMISSION - " + str(errors))
    return render_template('index.html',form=form, num_movies=num_movies)

@app.route('/all_movies')
def see_all_movies():
    themovielist=[]
    allmoviesq= Movie.query.all()
    search = tmdb.Search()
    for x in allmoviesq:
        useridmovie = x.user_id
        userrow = User.query.filter_by(userId=useridmovie).first()
        displaynamehere = userrow.userDisplay_name
        usernameusername = userrow.userUsername
        search = tmdb.Search()
        response = search.movie(query=x.movieText)
        movierating = response["results"][0]["vote_average"]
        ratingten = movierating * 10
        themovielist.append((x.movieText, displaynamehere, usernameusername, ratingten))
    return render_template ("all_movies.html", all_movies=themovielist)


@app.route('/all_users')
def see_all_users():
    user1 = User.query.all()
    allmoviesq= Movie.query.all()
    return render_template ("all_users.html", users=user1)

#HIGHEST RATING
@app.route ('/highest_rate')
def highest_rate():
    hirate_q = Movie.query.all()
    longboy = 0
    alistofstuff = []
    movietitle = ""
    displaynamehere = ""
    for x in hirate_q:
        useridmovie = x.user_id
        userrow = User.query.filter_by(userId=useridmovie).first()
        usernameusername = userrow.userUsername
        hellonewnums = int(usernameusername)
        if hellonewnums > longboy:
            longboy = hellonewnums
            displaynamehere = userrow.userDisplay_name
            movietitle = x.movieText
    alistofstuff.append((longboy, movietitle, displaynamehere))
    return render_template ("highest_rate.html", alistofstuff = alistofstuff)

if __name__ == '__main__':
    db.create_all() # Will create any defined models when you run the application
    app.run(use_reloader=True,debug=True) # The usual
