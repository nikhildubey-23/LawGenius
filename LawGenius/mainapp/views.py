from django.shortcuts import render, redirect
from django.http import JsonResponse
import os
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
import re
import logging
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.conf import settings

load_dotenv()

GROQ_API_KEY = os.getenv('GROQ_API_KEY')
DATABASE_PATH = os.path.join(settings.BASE_DIR, 'database.db')

def create_database():
    try:
        # Create the database directory if it doesn't exist
        os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
        
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        
        # Create user_history table if it doesn't exist
        c.execute('''CREATE TABLE IF NOT EXISTS user_history
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                     user_id INTEGER,
                     question TEXT, 
                     answer TEXT, 
                     timestamp TEXT)''')
        
        # Create an index on user_id for faster queries
        c.execute('''CREATE INDEX IF NOT EXISTS idx_user_id 
                    ON user_history(user_id)''')
        
        conn.commit()
        conn.close()
        logging.info("Database created successfully")
    except Exception as e:
        logging.error(f"Error creating database: {e}")
        raise

def save_to_history(user_id, question, answer):
    try:
        # Ensure database exists
        if not os.path.exists(DATABASE_PATH):
            create_database()
            
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Insert the history record
        c.execute("INSERT INTO user_history (user_id, question, answer, timestamp) VALUES (?, ?, ?, ?)", 
                  (user_id, question, answer, timestamp))
        
        conn.commit()
        conn.close()
        logging.info(f"History saved successfully for user {user_id}")
    except Exception as e:
        logging.error(f"Error saving to history: {e}")
        raise

def view_history(user_id):
    try:
        # Ensure database exists
        if not os.path.exists(DATABASE_PATH):
            create_database()
            
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        
        # Get history records for the user
        c.execute("SELECT id, user_id, question, answer, timestamp FROM user_history WHERE user_id = ? ORDER BY timestamp DESC", (user_id,))
        rows = c.fetchall()
        
        # Convert rows to a more readable format
        history = []
        for row in rows:
            history.append({
                'id': row[0],
                'user_id': row[1],
                'question': row[2],
                'answer': row[3],
                'timestamp': row[4]
            })
            
        conn.close()
        return history
    except Exception as e:
        logging.error(f"Error viewing history: {e}")
        return []

@csrf_exempt
@login_required
def clear_history(request):
    if request.method == 'POST':
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            c = conn.cursor()
            c.execute("DELETE FROM user_history WHERE user_id = ?", (request.user.id,))
            conn.commit()
            conn.close()
            messages.success(request, "Your history has been cleared successfully.")
            return redirect('view_history')
        except Exception as e:
            logging.error(f"Error clearing history: {e}")
            messages.error(request, "An error occurred while clearing your history.")
            return redirect('view_history')
    return redirect('view_history')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')

def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 != password2:
            messages.error(request, "Passwords don't match.")
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect('signup')

        try:
            user = User.objects.create_user(username=username, email=email, password=password1)
            user.save()
            login(request, user)
            return redirect('index')
        except Exception as e:
            messages.error(request, f"Error creating user: {str(e)}")
            return redirect('signup')

    return render(request, 'signup.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def index(request):
    try:
        if not os.path.exists(DATABASE_PATH):
            create_database()

        output = None
        output_language = "plaintext"
        if request.method == 'POST':
            try:
                user_input = request.POST['user_input']
                llm = ChatGroq(
                    temperature=0, 
                    groq_api_key=GROQ_API_KEY, 
                    model_name="deepseek-r1-distill-llama-70b"
                )
                prompt_template = create_prompt()
                chain_extract = prompt_template | llm 
                res = chain_extract.invoke(user_input)
                output = re.sub(r'<think>.*?</think>', '', res.content, flags=re.DOTALL).strip()

                def replace_double_asterisks(match):
                    text = match.group(0)
                    return re.sub(r'\*\*(.*?)\*\*', r'<h2>\1</h2>', text)

                output = re.sub(r'(?s)(```.*?```|[^`]+)', replace_double_asterisks, output)
                output = re.sub(r'```(\w+)\n(.*?)```', r'<pre><code class="language-\1">\2</code></pre>', output, flags=re.DOTALL)

                save_to_history(request.user.id, user_input, output)
                return render(request, 'index.html', {
                    'history': view_history(request.user.id), 
                    'output': output, 
                    'output_language': output_language,
                    'user': request.user
                })
            except Exception as e:
                logging.error(f"Error processing request: {e}")
                return JsonResponse({"error": str(e)}, status=500)

        return render(request, 'index.html', {
            'history': view_history(request.user.id), 
            'output': output, 
            'output_language': output_language,
            'user': request.user
        })
    except Exception as e:
        logging.error(f"Error in index view: {e}")
        messages.error(request, "An error occurred. Please try again.")
        return redirect('login')

@login_required
def view_history_page(request):
    try:
        return render(request, 'history.html', {
            'history': view_history(request.user.id),
            'user': request.user
        })
    except Exception as e:
        logging.error(f"Error in view_history_page: {e}")
        messages.error(request, "An error occurred while viewing history.")
        return redirect('index')

@login_required
def clear(request):
    try:
        clear_history(request)
        return redirect('index')
    except Exception as e:
        logging.error(f"Error in clear: {e}")
        messages.error(request, "An error occurred while clearing history.")
        return redirect('index')

@login_required
def about(request):
    return render(request, 'about.html', {'user': request.user})

@login_required
def reachout(request):
    return render(request, 'reachout.html', {'user': request.user})

def create_prompt():
    prompt_template = """
Welcome to LawGenius:
This platform is designed to assist users with various security-related queries and provide insights into offensive security techniques.

Benefits of This Tool:
- For Lawyers:
    - Fast research on laws and case decisions.
    - Case prediction using AI analysis of past cases.
    - Document analysis for contracts and agreements.
- For Law Students:
    - Helps in legal studies by explaining case laws, IPC, and CRPC.
    - Mock court preparation with AI simulations.
    - Quick resolution of legal queries.
- For Common People:
    - Legal information in Hindi for better understanding.
    - Free legal guidance for small cases.
    - Information on government schemes and RTI/FIR processes.
- For Judiciary:
    - Analysis of old cases for trends and insights.
    - Faster trials by reviewing small cases with AI.
- For Companies and Startups:
    - Legal due diligence for documents.
    - Risk analysis and error detection in contracts.

Developer: Aditi

Please respond to the following prompt:
{input}
"""
    return PromptTemplate.from_template(prompt_template)