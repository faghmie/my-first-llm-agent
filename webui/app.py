import os
import sys
import uuid
import yaml
import json

from flask import Flask, render_template, request, redirect, url_for, jsonify, Response
from dotenv import load_dotenv
import subprocess


# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Can only import after the sys.path manipulation
from agent import load_agent_config
from agent import Agent

load_dotenv()

app = Flask(__name__)
PROMPTS_DIR = os.getenv('PROMPTS_DIR', 'agent_scripts')

# Ensure prompts directory exists
os.makedirs(PROMPTS_DIR, exist_ok=True)

tasks = {}

def get_prompts():
    prompts = []
    for filename in os.listdir(PROMPTS_DIR):
        if filename.endswith('.yml'):
            path = os.path.join(PROMPTS_DIR, filename)
            config = load_agent_config(path)

            prompts.append({
                'name': filename[:-4],
                'content': f"{config.agent.description}\n\n{config.model.name} ({config.model.provider})"
            })
    
    prompts = sorted(prompts, key=lambda x: x["name"])

    return prompts

@app.route('/')
def index():
    prompts = get_prompts()
    return render_template('index.html', prompts=prompts)

@app.route('/add', methods=['GET', 'POST'])
def add_prompt():
    if request.method == 'POST':
        name = request.form['name'].strip().replace(' ', '_').lower()
        content = request.form['content']
        
        filename = f"{name}.yml"
        filepath = os.path.join(PROMPTS_DIR, filename)
        
        with open(filepath, 'w') as f:
            f.write(content)
        
        return redirect(url_for('index'))
    else:
        file = f'{PROMPTS_DIR}/_00_agent_template_prompt.yml'
        with open(file, 'r') as f:
            content = f.read()

    return render_template('add.html', content=content)

@app.route('/edit/<name>', methods=['GET', 'POST'])
def edit_prompt(name):
    filename = f"{name}.yml"
    filepath = os.path.join(PROMPTS_DIR, filename)
    
    if request.method == 'POST':
        content = request.form['content']
        with open(filepath, 'w') as f:
            f.write(content)
        return redirect(url_for('index'))
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    return render_template(
        'edit.html', 
        name=name, 
        content=content
    )

# Add these new routes
@app.route('/run/<agent_name>/input')
def run_input(agent_name):
    return render_template('input.html', agent_name=agent_name)

@app.route('/api/agent/<agent_name>', methods=['GET'])
def agent_details(agent_name):
    filename = f"{agent_name}.yml"
    filepath = os.path.join(PROMPTS_DIR, filename)
    
    with open(filepath, 'r') as f:
        yaml_obj = yaml.safe_load(f) 
        json_str = json.dumps(yaml_obj)
    
    return Response(json_str, mimetype='application/json')

@app.route('/start_task', methods=['POST'])
def start_task(): 
    agent_name = request.form['agent_name']
    user_prompt = request.form['user_prompt']

    filename = f"{agent_name}.yml"
    filepath = os.path.join(PROMPTS_DIR, filename)
    task_id = execute_agent(agent_name, filepath, user_prompt)
    return redirect(url_for('view_result',  task_id=task_id))

@app.route('/results/<task_id>')
def view_result(task_id):
    return render_template('result.html', task_id=task_id)


# Modify execute_agent function
def execute_agent(agent_name, filepath, user_prompt):
    """Long-running task simulation"""
    task_id = str(uuid.uuid4())
    agent = Agent()
    agent.run_async(filepath, user_prompt)

    tasks[task_id] = {
        'status': 'running',
        'output': 'Agent started....',
        'name': agent_name,
        'stream_index': 0,
        'user_prompt': user_prompt,
        'process': agent
    }
    return task_id

# Update check_status route to include user_prompt
@app.route('/status/<task_id>')
def check_status(task_id):
    task = tasks.get(task_id)
    if not task:
        return jsonify({'status': 'error', 'message': 'Task not found'})
    
    agent = task['process']
    current_index = task['stream_index']
    max_index = len(agent.stream_chunks)
    content = ""
    for i in range(current_index, max_index):
        task['stream_index'] = i + 1
        content += agent.stream_chunks[i]
        
    if not agent.is_done():
        return jsonify({
            'status': 'running',
            'name': task['name'],
            'output': content,
            'user_prompt': task['user_prompt']
        })
    
    output = agent.get_result()
    task['status'] = 'completed'
    task['output'] = output
    return jsonify({
        'status': 'completed',
        'output': output,
        'name': task['name'],
        'user_prompt': task['user_prompt']
    })
    
if __name__ == '__main__':
    app.run(debug=True)