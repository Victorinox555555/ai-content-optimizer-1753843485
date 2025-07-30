#!/usr/bin/env python3
"""
AI-Powered Content Optimizer MVP
Complete Flask application with authentication, payments, and AI optimization
"""

import os
import sqlite3
import hashlib
import secrets
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import stripe
import openai
from dotenv import load_dotenv

# Load environment variables from QWEN-GPT-AGI directory
load_dotenv('/home/ubuntu/QWEN-GPT-AGI/.env')
load_dotenv('/home/ubuntu/QWEN-GPT-AGI/env.txt')
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'ai-content-optimizer-secret-key-2025')

app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = False  # Allow JavaScript access for debugging
app.config['SESSION_COOKIE_SAMESITE'] = None  # More permissive for tunnel URLs
app.config['SESSION_COOKIE_DOMAIN'] = None  # Don't restrict domain

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

from openai import OpenAI
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
print(f"OpenAI API Key loaded: {'Yes' if os.getenv('OPENAI_API_KEY') else 'No'}")
if os.getenv('OPENAI_API_KEY'):
    print(f"API Key starts with: {os.getenv('OPENAI_API_KEY')[:10]}...")

def init_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            plan TEXT DEFAULT 'free',
            usage_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

@app.after_request
def add_security_headers(response):
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Content-Security-Policy'] = "default-src 'self' 'unsafe-inline' 'unsafe-eval' https://js.stripe.com https://checkout.stripe.com https://cdn.tailwindcss.com https://cdnjs.cloudflare.com"
    return response

@app.route('/')
def index():
    """Landing page"""
    return render_template('index.html')

@app.route('/login')
def login_page():
    """Login page"""
    return render_template('login.html')

@app.route('/signup')
def signup_page():
    """Signup page"""
    return render_template('signup.html')

@app.route('/pricing')
def pricing():
    """Pricing page"""
    return render_template('pricing.html')

@app.route('/dashboard')
def dashboard():
    """User dashboard with AI content optimization"""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT email, plan, usage_count FROM users WHERE id = ?', (session['user_id'],))
    user_data = cursor.fetchone()
    conn.close()
    
    if not user_data:
        session.clear()
        return redirect(url_for('login_page'))
    
    email, plan, usage_count = user_data
    
    return render_template('dashboard.html', 
                         email=email, 
                         plan=plan, 
                         usage_count=usage_count)

@app.route('/api/signup', methods=['POST'])
def api_signup():
    """User signup API"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'success': False, 'error': 'Email and password required'}), 400
        
        if len(password) < 6:
            return jsonify({'success': False, 'error': 'Password must be at least 6 characters'}), 400
        
        password_hash = generate_password_hash(password, method='pbkdf2:sha256')
        
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        
        try:
            cursor.execute('INSERT INTO users (email, password_hash) VALUES (?, ?)', 
                         (email, password_hash))
            conn.commit()
            user_id = cursor.lastrowid
            
            session['user_id'] = user_id
            session['email'] = email
            
            return jsonify({'success': True, 'message': 'Account created successfully'})
            
        except sqlite3.IntegrityError:
            return jsonify({'success': False, 'error': 'Email already exists'}), 400
        finally:
            conn.close()
            
    except Exception as e:
        return jsonify({'success': False, 'error': 'Server error'}), 500

@app.route('/api/login', methods=['POST'])
def api_login():
    """User login API"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'success': False, 'error': 'Email and password required'}), 400
        
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, password_hash FROM users WHERE email = ?', (email,))
        user_data = cursor.fetchone()
        conn.close()
        
        if not user_data or not check_password_hash(user_data[1], password):
            return jsonify({'success': False, 'error': 'Invalid email or password'}), 401
        
        session['user_id'] = user_data[0]
        session['email'] = email
        
        return jsonify({'success': True, 'message': 'Login successful'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': 'Server error'}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/api/session-debug')
def session_debug():
    """Debug session state"""
    return jsonify({
        'session_data': dict(session),
        'has_user_id': 'user_id' in session,
        'cookies': dict(request.cookies),
        'headers': dict(request.headers)
    })

@app.route('/api/optimize', methods=['POST'])
def optimize_content():
    """AI content optimization endpoint"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Authentication required'}), 401
    
    try:
        data = request.get_json()
        content = data.get('content', '').strip()
        target_audience = data.get('target_audience', 'General')
        
        if not content:
            return jsonify({'success': False, 'error': 'Content is required'}), 400
        
        if len(content) > 5000:
            return jsonify({'success': False, 'error': 'Content too long (max 5000 characters)'}), 400
        
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT plan, usage_count FROM users WHERE id = ?', (session['user_id'],))
        user_data = cursor.fetchone()
        
        if not user_data:
            conn.close()
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        plan, usage_count = user_data
        
        if plan == 'free' and usage_count >= 5:
            conn.close()
            return jsonify({'success': False, 'error': 'Free plan limit reached. Upgrade to continue.'}), 403
        elif plan == 'basic' and usage_count >= 100:
            conn.close()
            return jsonify({'success': False, 'error': 'Monthly limit reached.'}), 403
        
        try:
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": f"You are an expert content optimizer. Optimize the given content for {target_audience} audience. Focus on engagement, clarity, and impact. Provide the optimized content and explain key improvements."
                    },
                    {
                        "role": "user",
                        "content": f"Optimize this content for {target_audience} audience:\n\n{content}"
                    }
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            optimized_content = response.choices[0].message.content.strip()
            
            engagement_score = min(100, max(50, 
                len(optimized_content.split()) * 2 + 
                optimized_content.count('!') * 5 + 
                optimized_content.count('?') * 3 +
                (80 if target_audience != 'General' else 60)
            ))
            
            improvements = [
                "Enhanced readability and flow",
                "Optimized for target audience engagement",
                "Improved call-to-action elements",
                "Better emotional resonance",
                "Clearer value proposition"
            ]
            
            cursor.execute('UPDATE users SET usage_count = usage_count + 1 WHERE id = ?', 
                         (session['user_id'],))
            conn.commit()
            conn.close()
            
            return jsonify({
                'success': True,
                'original_content': content,
                'optimized_content': optimized_content,
                'engagement_score': engagement_score,
                'improvements': improvements,
                'usage_count': usage_count + 1
            })
            
        except Exception as openai_error:
            conn.close()
            return jsonify({'success': False, 'error': f'AI optimization failed: {str(openai_error)}'}), 500
        
    except Exception as e:
        return jsonify({'success': False, 'error': 'Server error'}), 500

@app.route('/api/create-checkout-session', methods=['POST'])
def create_checkout_session():
    """Create Stripe checkout session"""
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': os.getenv('PRICE_ID', 'price_1RcdcyEfbTvI2h4o4PVLTykg'),
                'quantity': 1,
            }],
            mode='subscription',
            success_url=request.host_url + 'dashboard?success=true',
            cancel_url=request.host_url + 'pricing?canceled=true',
            client_reference_id=str(session['user_id'])
        )
        
        return jsonify({'checkout_url': checkout_session.url})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhooks"""
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.getenv('STRIPE_WEBHOOK_SECRET', '')
        )
    except ValueError:
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError:
        return 'Invalid signature', 400
    
    if event['type'] == 'checkout.session.completed':
        session_data = event['data']['object']
        user_id = session_data.get('client_reference_id')
        
        if user_id:
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET plan = ? WHERE id = ?', ('basic', int(user_id)))
            conn.commit()
            conn.close()
    
    return 'Success', 200

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
