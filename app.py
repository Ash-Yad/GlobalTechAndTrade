import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import secrets
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify

# ==========================================
# 1. CONFIGURATION & PATH SETUP
# ==========================================

# CRITICAL FIX: Ensure templates AND static are found regardless of where Gunicorn starts
current_directory = os.path.dirname(os.path.abspath(__file__))
template_folder_path = os.path.join(current_directory, 'templates')
static_folder_path = os.path.join(current_directory, 'static')

# Initialize Flask app with explicit static and template folder paths
app = Flask(__name__,
            template_folder=template_folder_path,
            static_folder=static_folder_path)

# FIX 1: Secret key now reads from environment variable (does NOT change on restart)
# Go to Render Dashboard → Environment → Add: SECRET_KEY = any-random-long-string
app.secret_key = os.environ.get('SECRET_KEY', 'fallback-only-for-local-dev-do-not-use-in-production')

# Log the path immediately
print(f"INFO:app:GlobalTech&Trade startup. Template path set to: {template_folder_path}")
print(f"INFO:app:GlobalTech&Trade startup. Static path set to: {static_folder_path}")

# FIX 2: SESSION_COOKIE_SECURE set to True because Render uses HTTPS
app.config.update(
    SESSION_COOKIE_SECURE=True,   # FIXED: Render uses HTTPS so this must be True
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=timedelta(days=7)
)

# Setup logging for production
if not app.debug:
    logging.basicConfig(level=logging.INFO)
    app.logger.setLevel(logging.INFO)

    # Add file handler for logs (optional)
    try:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/globaltech.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
    except:
        pass  # If can't write logs, continue anyway
else:
    logging.basicConfig(level=logging.DEBUG)


# --- CONTEXT PROCESSORS ---

@app.context_processor
def inject_now():
    """Inject current year and datetime into all templates"""
    return dict(
        current_year=datetime.now().year,
        now=datetime.now
    )


# --- ERROR HANDLERS ---

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    app.logger.error(f'Server Error: {e}')
    return render_template('500.html'), 500


# --- MAIN NAVIGATION ROUTES ---

@app.route('/')
def index():
    """Home page route"""
    featured_services = [
        {
            'name': 'Mobile Applications',
            'icon': 'mobile-alt',
            'url': '/mobile-app-development',
            'description': 'Native iOS & Android apps'
        },
        {
            'name': 'Web Applications',
            'icon': 'globe',
            'url': '/web-application-development',
            'description': 'Modern scalable platforms'
        },
        {
            'name': 'Graphic Design',
            'icon': 'paint-brush',
            'url': '/graphic-design',
            'description': 'UI/UX & Branding'
        },
        {
            'name': 'Import/Export',
            'icon': 'ship',
            'url': '/import-export',
            'description': 'Global trade logistics'
        }
    ]

    return render_template(
        'home.html',
        title='GlobalTech&Trade | AI Solutions & Global Trade',
        active='home',
        featured_services=featured_services
    )


@app.route('/about')
def about():
    """About us page route"""
    milestones = [
        {
            'year': '2021',
            'title': 'Foundation',
            'badge': 'Foundation',
            'desc': 'Established in India And Zambia, focusing on Enterprise Software and IT Infrastructure.',
            'detail': 'IT Division Launched'
        },
        {
            'year': '2021',
            'title': 'Expansion',
            'badge': 'Expansion',
            'desc': 'Opened our Lusaka, Zambia HQ to facilitate Import/Export corridors and local tech support.',
            'detail': 'Trade Division Launched'
        },
        {
            'year': '2024',
            'title': 'Present',
            'badge': 'Present',
            'desc': 'Growing as a 360° partner for businesses looking to scale through AI and Global Trade.',
            'detail': 'Global Scale Achieved'
        }
    ]

    offices = [
        {
            'region': 'India',
            'country': 'India',
            'city': 'Noida',
            'full_address': 'Sector 63, Noida, Uttar Pradesh 201301',
            'phone': '+91 9027125341',
            'email': 'india@globaltechtrade.com',
            'division': 'IT Innovation Hub',
            'tags': ['Mobile Apps', 'Web Apps', 'AI/ML'],
            'flag': '🇮🇳',
            'badge_color': 'primary'
        },
        {
            'region': 'Zambia',
            'country': 'Zambia',
            'city': 'Lusaka',
            'full_address': 'Plot #10424/4, Cassanova Court, Chainama, Lusaka',
            'phone': '+260 97 7588581',
            'email': 'africa@globaltechtrade.com',
            'division': 'Trade & Logistics Hub',
            'tags': ['Customs', 'Freight', 'Logistics'],
            'flag': '🇿🇲',
            'badge_color': 'secondary'
        }
    ]

    return render_template(
        'about.html',
        title='About Us - GlobalTech&Trade',
        active='about',
        milestones=milestones,
        offices=offices
    )


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page with form handling"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        company = request.form.get('company', '').strip()
        service = request.form.get('service', 'General Services')
        message = request.form.get('message', '').strip()

        # Basic Validation
        if not name or not email or '@' not in email or not message:
            flash('Please fill in all required fields correctly.', 'error')
        else:
            # Log the inquiry
            app.logger.info(f'Contact Form: {name} ({email}) - Service: {service}')
            flash(f'Thank you {name}! Our team will contact you shortly regarding your inquiry.', 'success')

    # Service options for the dropdown
    services_list = [
        'IT Infrastructure & AI',
        'Import / Export Logistics',
        'Customs & Compliance',
        'Mobile Application Development',
        'Web Application Development',
        'Graphic Design Services',
        'Company Management',
        'General Services & Supply',
        'General Partnership'
    ]

    return render_template(
        'contact.html',
        title='Contact Us - GlobalTech&Trade',
        active='contact',
        services_list=services_list
    )


# --- IT SOLUTIONS ROUTES ---

@app.route('/it-solutions')
def it_solutions():
    """IT Solutions overview page"""
    services = [
        {
            'title': 'Mobile Applications',
            'desc': 'Native iOS & Android apps with exceptional user experiences and cutting-edge features.',
            'icon': 'mobile-alt',
            'link': '/mobile-app-development',
            'color': 'primary',
            'features': ['iOS (Swift) & Android (Kotlin)', 'Cross-platform (React Native)']
        },
        {
            'title': 'Web Applications',
            'desc': 'Scalable web solutions built with modern frameworks and cloud architecture.',
            'icon': 'globe',
            'link': '/web-application-development',
            'color': 'secondary',
            'features': ['React, Next.js, Vue.js', 'Node.js, Python, PHP']
        },
        {
            'title': 'Graphic Design',
            'desc': 'Creative design solutions that make your brand stand out from the competition.',
            'icon': 'paint-brush',
            'link': '/graphic-design',
            'color': 'accent',
            'features': ['UI/UX Design', 'Brand Identity']
        }
    ]

    return render_template(
        'it_solutions.html',
        title='IT Solutions - GlobalTech&Trade',
        active='it-solutions',
        services=services
    )


@app.route('/mobile-app-development')
def mobile_app_development():
    """Mobile App Development specific page"""
    features = [
        'Native iOS Development (Swift)',
        'Native Android Development (Kotlin)',
        'Cross-platform Solutions (React Native, Flutter)',
        'App Store & Google Play Deployment',
        'UI/UX Design for Mobile',
        'Push Notifications',
        'Offline Capability'
    ]
    return render_template(
        'mobile_app.html',
        title='Mobile App Development - GlobalTech&Trade',
        active='it-solutions',
        features=features
    )


@app.route('/web-application-development')
def web_application_development():
    """Web App Development specific page"""
    features = [
        'Modern Frontend Frameworks (React, Vue)',
        'Scalable Backend Architecture (Node, Python)',
        'Cloud Deployment (AWS, Azure)',
        'API Development & Integration',
        'Progressive Web Apps (PWA)',
        'Real-time Data Sync'
    ]
    return render_template(
        'web_app.html',
        title='Web App Development - GlobalTech&Trade',
        active='it-solutions',
        features=features
    )


@app.route('/graphic-design')
def graphic_design():
    """Graphic Design specific page"""
    services = [
        'Logo & Brand Identity Design',
        'UI/UX Interface Design',
        'Marketing Materials & Brochures',
        'Social Media Graphics',
        'Packaging Design',
        'Corporate Presentation Design'
    ]
    return render_template(
        'graphic_design.html',
        title='Graphic Design Services - GlobalTech&Trade',
        active='it-solutions',
        services=services
    )


# --- IMPORT/EXPORT ROUTES ---

@app.route('/import-export')
def import_export():
    """Import/Export overview page"""
    routes = [
        {
            'id': 'ROUTE_01',
            'title': 'India → Africa Corridor',
            'badge_origin': 'IN',
            'badge_dest': 'AF',
            'desc': 'Primary flow for Pharmaceuticals, Industrial Machinery, Textiles, and Agri-tech.',
            'transit_time': '18-22 Days',
            'active_ships': '12',
            'efficiency': 96,
            'next_departure': '2h'
        },
        {
            'id': 'ROUTE_02',
            'title': 'Africa → India Corridor',
            'badge_origin': 'AF',
            'badge_dest': 'IN',
            'desc': 'Strategic export of raw minerals, precious metals, agricultural products, and gemstones.',
            'transit_time': '20-24 Days',
            'active_ships': '10',
            'efficiency': 94,
            'next_departure': '6h'
        }
    ]

    services = [
        {
            'title': 'Customs Engineering',
            'desc': 'HS Code classification, duty optimization, and automated customs documentation.',
            'icon': 'file-invoice-dollar',
            'color': 'primary',
            'tags': ['AI-Powered', 'Real-time']
        },
        {
            'title': 'Direct Sourcing',
            'desc': 'Connect directly with verified Tier-1 manufacturers in India for bulk procurement.',
            'icon': 'search-dollar',
            'color': 'secondary',
            'tags': ['Verified Partners', 'Bulk Pricing']
        },
        {
            'title': 'Multimodal Freight',
            'desc': 'Integrated Sea, Air, and Road transport with real-time GPS tracking.',
            'icon': 'box',
            'color': 'accent',
            'tags': ['GPS Tracking', 'Temperature Control']
        },
        {
            'title': 'Smart Warehousing',
            'desc': 'Bonded warehousing in strategic transit hubs with digital inventory management.',
            'icon': 'boxes',
            'color': 'primary',
            'tags': ['Bonded', '24/7 Security']
        }
    ]

    return render_template(
        'import_export.html',
        title='Import/Export - GlobalTech&Trade',
        active='import-export',
        routes=routes,
        services=services
    )


# --- SERVICES HUB & OTHERS ---

@app.route('/services')
def services():
    """Main Services Hub Page"""
    categories = [
        {
            'title': 'IT Solutions',
            'desc': 'Web, Mobile, and Cloud infrastructure for modern businesses.',
            'icon': 'laptop-code',
            'url': '/it-solutions',
            'color': 'primary',
            'items': ['Mobile Apps', 'Web Apps', 'Graphic Design']
        },
        {
            'title': 'Import/Export',
            'desc': 'Technology-powered global trade solutions connecting Africa and Asia.',
            'icon': 'ship',
            'url': '/import-export',
            'color': 'secondary',
            'items': ['Customs', 'Freight', 'Sourcing']
        },
        {
            'title': 'Company Management',
            'desc': 'Business registration, compliance, and operational support.',
            'icon': 'building',
            'url': '/company-management',
            'color': 'accent',
            'items': ['Registration', 'Tax', 'Payroll']
        },
        {
            'title': 'General Services',
            'desc': 'Procurement, logistics, and supply chain solutions.',
            'icon': 'truck',
            'url': '/general-services',
            'color': 'primary',
            'items': ['Procurement', 'Logistics', 'Supply Chain']
        }
    ]

    return render_template(
        'services.html',
        title='All Services - GlobalTech&Trade',
        active='services',
        categories=categories
    )


@app.route('/company-management')
def company_management():
    """Company Management Page"""
    services_list = [
        'Business Registration & Incorporation',
        'Tax Registration & Compliance',
        'Work Permits & Visas',
        'Company Secretarial Services',
        'Accounting & Bookkeeping',
        'Payroll Management',
        'Regulatory Compliance'
    ]
    return render_template(
        'company_management.html',
        title='Company Management - GlobalTech&Trade',
        active='services',
        services_list=services_list
    )


@app.route('/general-services')
def general_services():
    """General Services Page"""
    services_list = [
        {'category': 'Procurement', 'items': ['Industrial Equipment', 'Office Supplies', 'Raw Materials']},
        {'category': 'Logistics', 'items': ['Transportation', 'Warehousing', 'Distribution']},
        {'category': 'Supply Chain', 'items': ['Supplier Sourcing', 'Quality Control', 'Order Processing']}
    ]
    return render_template(
        'general_services.html',
        title='General Services - GlobalTech&Trade',
        active='services',
        services_list=services_list
    )


# --- UTILITY ROUTES ---

@app.route('/health')
def health_check():
    """Simple health check for UptimeRobot monitoring - keeps site alive"""
    return {'status': 'healthy', 'timestamp': datetime.now().isoformat()}


# --- CHATBOT EMAIL API ---

@app.route('/api/send-demo-confirmation', methods=['POST'])
def send_demo_confirmation():
    """Send confirmation email to visitor after demo booking"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        visitor_email = data.get('email', '').strip()
        visitor_name = data.get('name', '').strip()
        phone = data.get('phone', '')
        company = data.get('company', '')
        service = data.get('service', '')
        message = data.get('message', 'None')
        
        if not visitor_email or '@' not in visitor_email:
            return jsonify({'success': False, 'error': 'Invalid email'}), 400
        
        # Email configuration - using Gmail SMTP (you can change this)
        # Set these environment variables in Render dashboard
        SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
        SMTP_EMAIL = os.environ.get('SMTP_EMAIL', 'info@globaltechandtrade.com')
        SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')  # App password for Gmail
        
        if not SMTP_PASSWORD:
            app.logger.warning('SMTP_PASSWORD not configured - skipping visitor email')
            return jsonify({'success': True, 'message': 'Email skipped - SMTP not configured'}), 200
        
        # Create beautiful HTML email
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7fa;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff;">
                <!-- Header -->
                <div style="background: linear-gradient(135deg, #0052CC 0%, #003D99 100%); padding: 30px; text-align: center;">
                    <h1 style="color: #ffffff; margin: 0; font-size: 24px;">GlobalTech&Trade</h1>
                    <p style="color: #93c5fd; margin: 10px 0 0 0; font-size: 14px;">IT Solutions & Import/Export Services</p>
                </div>
                
                <!-- Content -->
                <div style="padding: 30px;">
                    <h2 style="color: #1e3a5f; margin-top: 0;">🎉 Demo Request Confirmed!</h2>
                    
                    <p style="color: #4a5568; font-size: 16px; line-height: 1.6;">
                        Dear <strong>{visitor_name}</strong>,
                    </p>
                    
                    <p style="color: #4a5568; font-size: 16px; line-height: 1.6;">
                        Thank you for booking a demo with GlobalTech&Trade! Your request has been received successfully.
                    </p>
                    
                    <!-- Booking Details Box -->
                    <div style="background-color: #f0f9ff; border-left: 4px solid #0052CC; padding: 20px; margin: 20px 0; border-radius: 0 8px 8px 0;">
                        <h3 style="color: #0052CC; margin-top: 0; font-size: 16px;">📋 Your Booking Details</h3>
                        <table style="width: 100%; border-collapse: collapse;">
                            <tr><td style="padding: 8px 0; color: #64748b;">Name:</td><td style="padding: 8px 0; color: #1e3a5f; font-weight: 600;">{visitor_name}</td></tr>
                            <tr><td style="padding: 8px 0; color: #64748b;">Email:</td><td style="padding: 8px 0; color: #1e3a5f; font-weight: 600;">{visitor_email}</td></tr>
                            <tr><td style="padding: 8px 0; color: #64748b;">Phone:</td><td style="padding: 8px 0; color: #1e3a5f; font-weight: 600;">{phone}</td></tr>
                            <tr><td style="padding: 8px 0; color: #64748b;">Company:</td><td style="padding: 8px 0; color: #1e3a5f; font-weight: 600;">{company}</td></tr>
                            <tr><td style="padding: 8px 0; color: #64748b;">Service:</td><td style="padding: 8px 0; color: #1e3a5f; font-weight: 600;">{service}</td></tr>
                            <tr><td style="padding: 8px 0; color: #64748b;">Message:</td><td style="padding: 8px 0; color: #1e3a5f;">{message}</td></tr>
                        </table>
                    </div>
                    
                    <!-- Next Steps -->
                    <div style="background-color: #f0fdf4; border-left: 4px solid #22c55e; padding: 20px; margin: 20px 0; border-radius: 0 8px 8px 0;">
                        <h3 style="color: #166534; margin-top: 0; font-size: 16px;">📞 What Happens Next?</h3>
                        <p style="color: #4a5568; margin: 0; line-height: 1.6;">
                            Our team will contact you within <strong>24 hours</strong> to schedule your personalized demo session.
                        </p>
                    </div>
                    
                    <!-- Contact Info -->
                    <div style="background-color: #fefce8; border-left: 4px solid #eab308; padding: 20px; margin: 20px 0; border-radius: 0 8px 8px 0;">
                        <h3 style="color: #854d0e; margin-top: 0; font-size: 16px;">📱 Contact Us Directly</h3>
                        <p style="color: #4a5568; margin: 0; line-height: 1.8;">
                            🇮🇳 India: <strong>+91 9027125341</strong><br>
                            🇿🇲 Zambia: <strong>+260 977 588 581</strong><br>
                            📧 Email: <strong>info@globaltechandtrade.com</strong><br>
                            🌐 Website: <strong>www.globaltechandtrade.com</strong>
                        </p>
                    </div>
                </div>
                
                <!-- Footer -->
                <div style="background-color: #1e3a5f; padding: 20px; text-align: center;">
                    <p style="color: #93c5fd; margin: 0; font-size: 14px;">
                        Thank you for choosing GlobalTech&Trade!
                    </p>
                    <p style="color: #64748b; margin: 10px 0 0 0; font-size: 12px;">
                        © {datetime.now().year} GlobalTech&Trade. All rights reserved.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Create email message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = '✅ Demo Request Confirmed - GlobalTech&Trade'
        msg['From'] = f'GlobalTech&Trade <{SMTP_EMAIL}>'
        msg['To'] = visitor_email
        
        # Plain text version
        text_content = f"""
Demo Request Confirmed - GlobalTech&Trade

Dear {visitor_name},

Thank you for booking a demo with GlobalTech&Trade! Your request has been received successfully.

YOUR BOOKING DETAILS:
- Name: {visitor_name}
- Email: {visitor_email}
- Phone: {phone}
- Company: {company}
- Service: {service}
- Message: {message}

WHAT HAPPENS NEXT?
Our team will contact you within 24 hours to schedule your personalized demo session.

CONTACT US:
India: +91 9027125341
Zambia: +260 977 588 581
Email: info@globaltechandtrade.com
Website: www.globaltechandtrade.com

Thank you for choosing GlobalTech&Trade!
        """
        
        msg.attach(MIMEText(text_content, 'plain'))
        msg.attach(MIMEText(html_content, 'html'))
        
        # Send email to visitor - try TLS first, then SSL
        email_sent = False
        try:
            # Try TLS (port 587)
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30) as server:
                server.starttls()
                server.login(SMTP_EMAIL, SMTP_PASSWORD)
                server.send_message(msg)
                email_sent = True
                app.logger.info(f'Email sent via TLS to: {visitor_email}')
        except Exception as tls_error:
            app.logger.warning(f'TLS failed: {tls_error}, trying SSL...')
            try:
                # Try SSL (port 465)
                import ssl
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL(SMTP_SERVER, 465, context=context, timeout=30) as server:
                    server.login(SMTP_EMAIL, SMTP_PASSWORD)
                    server.send_message(msg)
                    email_sent = True
                    app.logger.info(f'Email sent via SSL to: {visitor_email}')
            except Exception as ssl_error:
                app.logger.error(f'SSL also failed: {ssl_error}')
                raise ssl_error
        
        if not email_sent:
            raise Exception('Failed to send email via both TLS and SSL')
        
        # Also send notification to company
        try:
            company_msg = MIMEMultipart('alternative')
            company_msg['Subject'] = f'🔔 New Demo Request - {visitor_name} ({service})'
            company_msg['From'] = f'GTT Chatbot <{SMTP_EMAIL}>'
            company_msg['To'] = SMTP_EMAIL  # Send to company email
            
            company_html = f"""
            <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2 style="color: #0052CC;">🔔 New Demo Request from Chatbot</h2>
                <table style="border-collapse: collapse; width: 100%; max-width: 500px;">
                    <tr><td style="padding: 10px; border: 1px solid #ddd; background: #f5f5f5;"><strong>Name</strong></td><td style="padding: 10px; border: 1px solid #ddd;">{visitor_name}</td></tr>
                    <tr><td style="padding: 10px; border: 1px solid #ddd; background: #f5f5f5;"><strong>Email</strong></td><td style="padding: 10px; border: 1px solid #ddd;">{visitor_email}</td></tr>
                    <tr><td style="padding: 10px; border: 1px solid #ddd; background: #f5f5f5;"><strong>Phone</strong></td><td style="padding: 10px; border: 1px solid #ddd;">{phone}</td></tr>
                    <tr><td style="padding: 10px; border: 1px solid #ddd; background: #f5f5f5;"><strong>Company</strong></td><td style="padding: 10px; border: 1px solid #ddd;">{company}</td></tr>
                    <tr><td style="padding: 10px; border: 1px solid #ddd; background: #f5f5f5;"><strong>Service</strong></td><td style="padding: 10px; border: 1px solid #ddd;">{service}</td></tr>
                    <tr><td style="padding: 10px; border: 1px solid #ddd; background: #f5f5f5;"><strong>Message</strong></td><td style="padding: 10px; border: 1px solid #ddd;">{message}</td></tr>
                    <tr><td style="padding: 10px; border: 1px solid #ddd; background: #f5f5f5;"><strong>Source</strong></td><td style="padding: 10px; border: 1px solid #ddd;">💬 Website Chatbot</td></tr>
                    <tr><td style="padding: 10px; border: 1px solid #ddd; background: #f5f5f5;"><strong>Time</strong></td><td style="padding: 10px; border: 1px solid #ddd;">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</td></tr>
                </table>
                <p style="margin-top: 20px; color: #666;">Please contact this lead within 24 hours.</p>
            </body>
            </html>
            """
            company_msg.attach(MIMEText(company_html, 'html'))
            
            try:
                with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30) as server:
                    server.starttls()
                    server.login(SMTP_EMAIL, SMTP_PASSWORD)
                    server.send_message(company_msg)
            except:
                import ssl
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL(SMTP_SERVER, 465, context=context, timeout=30) as server:
                    server.login(SMTP_EMAIL, SMTP_PASSWORD)
                    server.send_message(company_msg)
            
            app.logger.info(f'Company notification sent for: {visitor_name}')
        except Exception as e:
            app.logger.error(f'Company email failed: {e}')
        
        return jsonify({'success': True, 'message': 'Email sent successfully'}), 200
        
    except smtplib.SMTPAuthenticationError as e:
        app.logger.error(f'SMTP Authentication failed: {e}')
        return jsonify({'success': False, 'error': 'Email authentication failed'}), 500
    except Exception as e:
        app.logger.error(f'Email sending error: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500


# --- MAIN ENTRY POINT (ONLY FOR LOCAL DEVELOPMENT) ---

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))

    print("=" * 60)
    print("🚀 GlobalTech&Trade Development Server Starting...")
    print(f"📍 Local URL: http://127.0.0.1:{port}")
    print("=" * 60)
    print("⚠️  For production, use: gunicorn app:app")
    print("=" * 60)

    app.run(debug=True, host='0.0.0.0', port=port)