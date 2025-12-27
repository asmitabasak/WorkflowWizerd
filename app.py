from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///workflow.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Models
class Workflow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    current_step_index = db.Column(db.Integer, default=0)
    tasks = db.relationship('Task', backref='workflow', cascade="all, delete-orphan")

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    workflow_id = db.Column(db.Integer, db.ForeignKey('workflow.id'))

# Initialize Database with a Sample Workflow
with app.app_context():
    db.create_all()
    if not Workflow.query.first():
        new_wf = Workflow(name="New Project Launch")
        db.session.add(new_wf)
        steps = ["Define Project Scope", "Market Research", "Build Prototype", "Launch Beta"]
        for s in steps:
            db.session.add(Task(description=s, workflow=new_wf))
        db.session.commit()

@app.route('/')
def index():
    workflows = Workflow.query.all()
    return render_template('index.html', workflows=workflows)

@app.route('/wizard/<int:wf_id>')
def wizard(wf_id):
    wf = Workflow.query.get_or_404(wf_id)
    # If workflow is complete
    if wf.current_step_index >= len(wf.tasks):
        return render_template('complete.html', wf=wf)
    
    current_task = wf.tasks[wf.current_step_index]
    progress = int((wf.current_step_index / len(wf.tasks)) * 100)
    return render_template('wizard.html', wf=wf, task=current_task, progress=progress)

@app.route('/next/<int:wf_id>')
def next_step(wf_id):
    wf = Workflow.query.get_or_404(wf_id)
    wf.current_step_index += 1
    db.session.commit()
    return redirect(url_for('wizard', wf_id=wf.id))

if __name__ == '__main__':
    app.run(debug=True)
