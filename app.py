from flask import Flask,render_template,redirect,request,url_for,session
import re
from extensions import db, mig
from models import user
from models import Skill,Education,Project,Link,Detail
from flask_login import LoginManager,login_user,logout_user,current_user,login_required
from flask_bcrypt import Bcrypt
import smtplib
import random
import os
from werkzeug.utils import secure_filename
import uuid





#___________________________________________________________________________

app=Flask(__name__,template_folder='Templates',static_folder='static',static_url_path='/')
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'img' )



app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

db.init_app(app)
mig.init_app(app,db)

#login manager side _______________________________________________

login_manager = LoginManager() 
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to see this page.'
#PDF_CONFIG = pdfkit.configuration(wkhtmltopdf="C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe")
@login_manager.user_loader
def load_user(uid):
    return user.query.get(uid)

#ermail setup_________________________________________________________
otp = str(random.randint(100000, 999999))
def emailverify(email,otp1):
    sender_email = 'adhilek1@gmail.com'        # Your email
    sender_password = 'unoc nxuq aaol nijw'  
    receiver_email = email
    otp = otp1
    subject = "Your OTP Code"
    body = f"Your OTP is: {otp}"
    message = f"Subject: {subject}\n\n{body}"
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, message)
        server.quit()
        return (f"OTP sent to {receiver_email}")
    except Exception as e:
       return ("Error sending email:", e)
        

#password bcrypt side_________________________________________________________

bcrypt = Bcrypt()
"""runig side"""
#url side______________________________________________________________________
@app.route('/')
def home():
 if current_user.is_authenticated:
    current_user2=current_user.username
    userd=Detail.query.filter_by(user_id=current_user2).first_or_404()
    return render_template('index.html',us=userd)
 else:
    return render_template('index.html')
    




@app.route('/register', methods=['GET', 'POST'])
def registetr():
   
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        if len(username) < 4 or not re.match(r'^[a-zA-Z0-9]+$', username):
         return render_template('register.html', list1=f"Invalid username! Username must be at least 4 characters, start with a letter, and contain only letters, numbers, or underscores.")
        al = "this username already taken!" 
        a2 = "this email already taken!"
        
        existing_user = user.query.filter_by(username=username).first()
        existing_email = user.query.filter_by(email=email).first()

        if existing_user and existing_email:
            return render_template('register.html', list1=f"{username} and {email} already taken!")
        elif existing_user:
            return render_template('register.html', list1=f"{username} {al}")
        elif existing_email:
            return render_template('register.html', list1=f"{email} {a2}")
        if len(password) < 8 or not re.search(r'\d', password) or not re.search(r'[A-Z]', password):
           return render_template('register.html',username=username,email=email, list1="Password must be at least 8 characters, include a digit and a capital letter")
        # Hash password and create user
        hash_password = bcrypt.generate_password_hash(password.encode('utf-8')).decode('utf-8')

        session['username'] = username
        session['email'] = email
        session['password'] = hash_password
        session['token'] = "13"
        return redirect(url_for('verfy'))

       

        
      
    
    return render_template('register.html')
 

@app.route('/verfy', methods=['POST', 'GET'])
def verfy():

    username = session.get('username')
    email = session.get('email')
    password = session.get('password')
    token = session.get('token')

    if not email:
            return redirect(url_for("registetr"))
    if request.method == 'GET':
    
        otp = str(random.randint(100000, 999999))
        session['otp'] = otp
        session['attempts'] = 3
        session['email'] = email


        emailverify(email=email, otp1=otp)
        
        return render_template('verfy.html', name=email)

    # POST starts here
    if request.method == 'POST':
        
        user_input = request.form['otp']
        correct_otp = session.get('otp')
        attempts_left = session.get('attempts', 0)
        email = session.get('email')
        token = session.get("token")
        if user_input == correct_otp:
          
            # Create related entries
            if  token=="13":
                new_user = user(username=username, email=email, password=password)
                db.session.add(new_user)
                db.session.commit()
                db.session.add(Skill(user_id=username))
                db.session.add(Education(user_id=username))
                db.session.add(Link(user_id=username))
                db.session.add(Project(user_id=username))
                db.session.add(Detail(user_id=username))
                db.session.commit()
                session.pop('otp', None)
                session.pop('attempts', None)
                session.pop('email', None)
                session.pop("token",None)
                return redirect('/login')
            elif token == "14":
                print("i am inside the box ")
                print(password)
                updated_user = user.query.filter_by(email=email).first()
                if updated_user:
                    updated_user.password = password  # already hashed in session
                    db.session.commit()

                    # Clear session data
                    session.pop('otp', None)
                    session.pop('attempts', None)
                    session.pop('email', None)
                    session.pop("token", None)
                    session.pop('username', None)
                    session.pop('password', None)

                    return redirect('/login')


            else:
                print(token)
                return "u got wrong tocken"
        attempts_left -= 1
        session['attempts'] = attempts_left

        if attempts_left <= 0:
           

            session.pop('otp', None)
            session.pop('attempts', None)
            session.pop('email', None)
            if token==13:
             return render_template('verfy.html', name=email, message=f'❌ User with email {email} has been deleted after failed OTP attempts. Please register again.')
            if token==14:
             return render_template('verfy.html', name=email, message=f'❌ User with email {email} has been unchanged password after failed OTP attempts.')
        return render_template('verfy.html', name=email, message=f'❌ Incorrect OTP. You have {attempts_left} attempt(s) left.')

             





    


   
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        userc = user.query.filter_by(username=username).first()

        if not userc or not bcrypt.check_password_hash(userc.password, password):
            # Generic message for either username or password failure
            return render_template('login.html', error="Username or password is incorrect.")

        login_user(userc)
        return redirect('/')  # or your homepage

    return render_template('login.html')

@app.route('/logout', methods=['POST','GET'])
def logout():
    logout_user()
    return redirect('/')


"""///////////////////////  working process ///////////////////////////////////////"""

@app.route('/form', methods=['GET', 'POST'])
@login_required
def edit_portfolio():

    user_id = current_user.username
    # Fetch existing entrie
    skills = Skill.query.filter_by(user_id=user_id).all()
    educations = Education.query.filter_by(user_id=user_id).all()
    projects = Project.query.filter_by(user_id=user_id).all()
    links = Link.query.filter_by(user_id=user_id).all()
    detail = Detail.query.filter_by(user_id=user_id).first()

    if request.method == 'POST':
        # Clear old data to simplify update (or use smarter update logic)
        Skill.query.filter_by(user_id=user_id).delete()
        Education.query.filter_by(user_id=user_id).delete()
        Project.query.filter_by(user_id=user_id).delete()
        Link.query.filter_by(user_id=user_id).delete()
        Detail.query.filter_by(user_id=user_id).delete()
        image_file = request.files.get('image')

        # Default to None or a default image if no file is uploaded
        image_filename = None

        if image_file and image_file.filename:
            image_filename = secure_filename(image_file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{image_filename}"
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            image_file.save(image_path)

        # Continue with other form data processing and saving to the database
        new_detail = Detail(
            name=request.form.get('name'),
            date_of_birth=request.form.get('dob'),
            prof=request.form.get('prof'),
            image_url=unique_filename,  # Will be None if no image uploaded
            description=request.form.get('description'),
            user_id=user_id,
            location=request.form.get('location'),
            phone_number=request.form.get('number')

        )
        db.session.add(new_detail)

        # === SKILLS ===
        skill_list = request.form.getlist('skills[]')
        for s in skill_list:
            if s.strip():
                db.session.add(Skill(name=s.strip(), user_id=user_id))

        # === EDUCATION ===
        degrees = request.form.getlist('degree[]')
        institutions = request.form.getlist('institution[]')
        years = request.form.getlist('year[]')
        for degree, inst, year in zip(degrees, institutions, years):
            db.session.add(Education(degree=degree, institution=inst, year=year, user_id=user_id))

        # === PROJECTS ===
        titles = request.form.getlist('project_title[]')
        descriptions = request.form.getlist('project_description[]')
        for t, d in zip(titles, descriptions):
            db.session.add(Project(title=t, description=d, user_id=user_id))

        # === LINKS ===
        link_types = request.form.getlist('link_type[]')
        urls = request.form.getlist('link_url[]')
        for lt, u in zip(link_types, urls):
            db.session.add(Link(type=lt, url=u, user_id=user_id))

        

        # === DETAIL === (update or insert)
      
    
          

        db.session.commit()
        return redirect('theame')

    return render_template('fourm.html', skill1=skills, educations=educations, projects=projects,
                           links=links, detail=detail)

  

    
@app.route('/theme')
@login_required
def theme():  
    user_id = current_user.username
    # Fetch existing entrie
    skills = Skill.query.filter_by(user_id=user_id).all()
    educations = Education.query.filter_by(user_id=user_id).all()
    projects = Project.query.filter_by(user_id=user_id).all()
    links = Link.query.filter_by(user_id=user_id).all()
    detail = Detail.query.filter_by(user_id=user_id).first()


    return render_template('th2.html',skills2=skills,educations=educations,projects=projects,links=links,detail=detail)

@app.route('/data')
@login_required
def data():  
    user_id = current_user.username
    # Fetch existing entrie
    skills = Skill.query.filter_by(user_id=user_id).all()
    educations = Education.query.filter_by(user_id=user_id).all()
    projects = Project.query.filter_by(user_id=user_id).all()
    links = Link.query.filter_by(user_id=user_id).all()
    detail = Detail.query.filter_by(user_id=user_id).first()


    return render_template('th2.html',skills2=skills,educations=educations,projects=projects,links=links,detail=detail)






@app.route('/sqluser')
def sql():
      
     users = user.query.all()
     for user11 in users:
         print(user11.uid, user11.email,user11.username,user11.password) 
     return "is ready"
@app.route('/sqlskill')
def sqlskill():
     skill = Skill.query.all()
     return render_template('sqlite.html',people=skill)


@app.route('/addvalue')
def addvalue():
    list=['a','s','f','b','d']
    for i in list:

        print(i)
    people = user.query.all()

    return render_template('sqlite.html',people=people)

@app.route('/forget', methods=['POST','GET'])
def forget():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        uservalid = user.query.filter_by(username=username).first()
        emailvalid =user.query.filter_by(email=email).first()
        if len(password) < 8 or not re.search(r'\d', password) or not re.search(r'[A-Z]', password):
           return render_template('forget.html', p="Password must be at least 8 characters, include a digit and a capital letter")
        # Hash password and create user
        hash_password = bcrypt.generate_password_hash(password.encode('utf-8')).decode('utf-8')
        if uservalid!=None :
           oo=uservalid.email
           session['username'] = username
           session['email'] = oo
           session['password'] =hash_password 
           session['token'] ="14"
           return redirect(url_for('verfy'))
          
        elif emailvalid!=None:
           oo=emailvalid.email
           session['username'] = username
           session['email'] = oo
           session['password'] =hash_password
           session['token'] ="14"
           return redirect(url_for('verfy'))
        
        else:
           return render_template('forget.html',p="you enter invlide data from our database")
 
    return render_template('forget.html')
@app.route('/resume/<theme_name>')
@login_required
def render_theme(theme_name):
    user_id = current_user.username  # This assumes 'username' is the user_id in your DB

    # Fetch user data
    skills = Skill.query.filter_by(user_id=user_id).all()
    educations = Education.query.filter_by(user_id=user_id).all()
    projects = Project.query.filter_by(user_id=user_id).all()
    links = Link.query.filter_by(user_id=user_id).all()
    detail = Detail.query.filter_by(user_id=user_id).first()

    try:
        # Dynamically render the selected theme's HTML template
        return render_template(
            f'theme/{theme_name}.html',
            skills2=skills,
            educations=educations,
            projects=projects,
            links=links,
            detail=detail
        )
    except:
        # If the template doesn't exist, fallback or show error
        return f"Theme '{theme_name}' not found.", 404
"""
@app.route('/download-pdf')
@login_required
def download_pdf():

    user_id = current_user.username
    # Fetch existing entrie
    skills = Skill.query.filter_by(user_id=user_id).all()
    educations = Education.query.filter_by(user_id=user_id).all()
    projects = Project.query.filter_by(user_id=user_id).all()
    links = Link.query.filter_by(user_id=user_id).all()
    detail = Detail.query.filter_by(user_id=user_id).first()


    
    # render HTML as string
    rendered = render_template('th2.html', skills2=skills, educations=educations, projects=projects, links=links, detail=detail)

    # generate PDF
    pdf = pdfkit.from_string(rendered, False, configuration=PDF_CONFIG)

    # return PDF as download
    return (
        pdf,
        200,
        {
            'Content-Type': 'application/pdf',
            'Content-Disposition': f'attachment; filename="{user_id}_portfolio.pdf"',
        }
    )

"""




if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000,debug=True)
