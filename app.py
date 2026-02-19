from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
from datetime import datetime, timedelta
import webbrowser
import threading
import time
import secrets
import uuid
import logging
from logging.handlers import RotatingFileHandler

# Initialize Flask app
app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# Configuration
app.config.update(
    SESSION_COOKIE_SECURE=False,  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=timedelta(days=7),
    MAX_CONTENT_LENGTH=16 * 1024 * 1024  # 16MB max file size
)

# Setup logging
if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/globaltech.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('GlobalTech&Trade startup')


# Context processors
@app.context_processor
def inject_current_year():
    """Inject current year into all templates"""
    return {'current_year': datetime.now().year}


@app.context_processor
def inject_utility_functions():
    """Inject utility functions into all templates"""

    def generate_id():
        return str(uuid.uuid4())[:8]

    def format_phone(phone):
        """Format phone numbers"""
        if phone:
            # Remove all non-numeric characters
            cleaned = ''.join(filter(str.isdigit, phone))
            if len(cleaned) == 10:
                return f"({cleaned[:3]}) {cleaned[3:6]}-{cleaned[6:]}"
            return phone
        return phone

    def format_currency(amount, currency='USD'):
        """Format currency amounts"""
        try:
            amount = float(amount)
            if currency == 'USD':
                return f"${amount:,.2f}"
            elif currency == 'INR':
                return f"₹{amount:,.2f}"
            elif currency == 'ZMW':
                return f"K{amount:,.2f}"
            return f"{amount:,.2f}"
        except (ValueError, TypeError):
            return amount

    return dict(
        generate_id=generate_id,
        format_phone=format_phone,
        format_currency=format_currency,
        enumerate=enumerate,
        len=len,
        str=str,
        int=int,
        float=float,
        now=datetime.now,
        today=datetime.now().date
    )


# Custom template filters
@app.template_filter('format_date')
def format_date_filter(date):
    """Format date for templates"""
    if isinstance(date, datetime):
        return date.strftime('%B %d, %Y')
    return date


@app.template_filter('format_datetime')
def format_datetime_filter(dt):
    """Format datetime for templates"""
    if isinstance(dt, datetime):
        return dt.strftime('%B %d, %Y at %I:%M %p')
    return dt


@app.template_filter('truncate_text')
def truncate_text(text, length=100):
    """Truncate text to specified length"""
    if not text or len(text) <= length:
        return text
    return text[:length].rsplit(' ', 1)[0] + '...'


@app.template_filter('slugify')
def slugify_filter(text):
    """Convert text to URL-friendly slug"""
    if not text:
        return ''
    # Convert to lowercase and replace spaces with hyphens
    slug = text.lower().replace(' ', '-')
    # Remove special characters
    slug = ''.join(e for e in slug if e.isalnum() or e == '-')
    # Remove multiple hyphens
    while '--' in slug:
        slug = slug.replace('--', '-')
    return slug.strip('-')


# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    app.logger.error(f'Page not found: {request.url}')
    return render_template('404.html',
                           title='Page Not Found',
                           error='The page you are looking for does not exist.',
                           active='404'), 404


@app.errorhandler(500)
def internal_server_error(e):
    """Handle 500 errors"""
    app.logger.error(f'Server error: {str(e)}')
    return render_template('500.html',
                           title='Server Error',
                           error='Something went wrong. Please try again later.',
                           active='500'), 500


# --- MAIN NAVIGATION ROUTES ---

@app.route('/')
def index():
    """Home page route"""
    # Track page visit
    if 'visits' not in session:
        session['visits'] = 0
    session['visits'] = session.get('visits', 0) + 1
    session['last_visit'] = datetime.now().isoformat()

    # Featured services for homepage
    featured_services = [
        {
            'name': 'Mobile Applications',
            'icon': 'mobile-alt',
            'url': '/mobile-app-development',
            'color': 'primary',
            'description': 'Native iOS & Android apps with cutting-edge features'
        },
        {
            'name': 'Web Applications',
            'icon': 'globe',
            'url': '/web-application-development',
            'color': 'secondary',
            'description': 'Scalable web solutions built with modern frameworks'
        },
        {
            'name': 'Graphic Design',
            'icon': 'paint-brush',
            'url': '/graphic-design',
            'color': 'accent',
            'description': 'Creative design that makes your brand stand out'
        },
        {
            'name': 'Import/Export',
            'icon': 'ship',
            'url': '/import-export',
            'color': 'primary',
            'description': 'End-to-end global trade solutions'
        }
    ]

    # Company stats
    stats = [
        {'value': '40+', 'label': 'Countries Served'},
        {'value': '10+', 'label': 'Years Experience'},
        {'value': '500+', 'label': 'Projects Completed'},
        {'value': '24/7', 'label': 'Support Available'}
    ]

    return render_template('home.html',
                           title='GlobalTech&Trade - AI Solutions & Global Trade',
                           active='home',
                           featured_services=featured_services,
                           stats=stats)


@app.route('/about')
def about():
    """About us page route"""
    # Team information
    team_info = {
        'india_office': {
            'established': 2014,
            'employees': 25,
            'specialization': 'IT Development & Software',
            'lead': 'Ashish Kumar',
            'email': 'india@globaltechtrade.com',
            'phone': '+91 9027125341'
        },
        'zambia_office': {
            'established': 2018,
            'employees': 15,
            'specialization': 'Trade & Logistics',
            'lead': 'Mr.Kelvin',
            'email': 'africa@globaltechtrade.com',
            'phone': '+260 97 7588581'
        }
    }

    # Company milestones
    milestones = [
        {'year': 2014, 'event': 'Founded in Noida, India', 'description': 'Started as an IT consulting firm'},
        {'year': 2016, 'event': 'Expanded to mobile development', 'description': 'Launched mobile app division'},
        {'year': 2018, 'event': 'Opened Zambia office', 'description': 'Established African presence in Lusaka'},
        {'year': 2020, 'event': 'Launched trade division', 'description': 'Added import/export services'},
        {'year': 2022, 'event': 'AI integration', 'description': 'Incorporated AI into all solutions'},
        {'year': 2024, 'event': 'Global expansion', 'description': 'Serving 40+ countries worldwide'}
    ]

    return render_template('about.html',
                           title='About Us - GlobalTech&Trade',
                           active='about',
                           team_info=team_info,
                           milestones=milestones)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page with form handling"""
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        company = request.form.get('company', '').strip()
        service = request.form.get('service', 'General Inquiry')
        message = request.form.get('message', '').strip()

        # Validation
        errors = []
        if not name:
            errors.append('Name is required')
        if not email or '@' not in email or '.' not in email:
            errors.append('Valid email address is required')
        if not message:
            errors.append('Message is required')
        elif len(message) < 10:
            errors.append('Message must be at least 10 characters long')

        if errors:
            for error in errors:
                flash(error, 'error')
        else:
            # Log the inquiry
            app.logger.info(f'Contact form submission - Name: {name}, Email: {email}, Service: {service}')

            # Here you would typically:
            # 1. Send email notification to sales team
            # 2. Save to database
            # 3. Add to CRM system
            # 4. Send auto-reply to customer

            # For demo purposes, just flash success message
            success_message = f'Thank you {name}! Your message has been received. Our team will respond within 24 hours.'
            if service != 'General Inquiry':
                success_message = f'Thank you for your interest in {service}, {name}! Our specialist will contact you shortly.'

            flash(success_message, 'success')

            # Store in session for demo
            session['last_inquiry'] = {
                'name': name,
                'service': service,
                'timestamp': datetime.now().isoformat()
            }

        return redirect(url_for('contact'))

    # Services list for dropdown
    services = [
        'General Inquiry',
        'Mobile Application Development',
        'Web Application Development',
        'Graphic Design Services',
        'Import/Export Services',
        'Company Management',
        'General Services & Supply',
        'Partnership Opportunities'
    ]

    return render_template('contact.html',
                           title='Contact Us - GlobalTech&Trade',
                           active='contact',
                           services=services)


# --- IT SOLUTION ROUTES ---

@app.route('/it-solutions')
def it_solutions():
    """IT Solutions overview page"""
    services = [
        {
            'title': 'Mobile Applications',
            'description': 'Native iOS and Android apps with exceptional user experiences. We build custom mobile solutions tailored to your business needs.',
            'icon': 'mobile-alt',
            'url': '/mobile-app-development',
            'color': 'primary',
            'features': ['iOS & Android Native', 'Cross-platform (React Native/Flutter)', 'App Store Optimization',
                         'Ongoing Support']
        },
        {
            'title': 'Web Applications',
            'description': 'Powerful, scalable web applications built with modern frameworks. From e-commerce to enterprise portals, we deliver solutions that work.',
            'icon': 'globe',
            'url': '/web-application-development',
            'color': 'secondary',
            'features': ['React & Next.js', 'Node.js & Python', 'Cloud Deployment', 'Progressive Web Apps']
        },
        {
            'title': 'Graphic Design',
            'description': 'Creative design solutions that make your brand stand out. We handle everything from UI/UX to complete brand identity.',
            'icon': 'paint-brush',
            'url': '/graphic-design',
            'color': 'accent',
            'features': ['UI/UX Design', 'Brand Identity', 'Marketing Materials', 'Social Media Graphics']
        }
    ]

    # Technologies we use
    technologies = [
        {'name': 'React', 'category': 'Frontend', 'proficiency': 95},
        {'name': 'Node.js', 'category': 'Backend', 'proficiency': 90},
        {'name': 'Python', 'category': 'Backend', 'proficiency': 85},
        {'name': 'Swift', 'category': 'iOS', 'proficiency': 90},
        {'name': 'Kotlin', 'category': 'Android', 'proficiency': 88},
        {'name': 'Flutter', 'category': 'Cross-platform', 'proficiency': 85}
    ]

    return render_template('it_solutions.html',
                           title='IT Solutions - GlobalTech&Trade',
                           active='it-solutions',
                           services=services,
                           technologies=technologies)


@app.route('/mobile-app-development')
def mobile_app_development():
    """Mobile app development page"""
    features = [
        'Native iOS Development (Swift)',
        'Native Android Development (Kotlin/Java)',
        'Cross-platform (React Native, Flutter)',
        'UI/UX Design for Mobile',
        'App Store & Google Play Deployment',
        'Ongoing Maintenance & Support',
        'Push Notifications',
        'Offline Functionality',
        'In-app Purchases',
        'Analytics Integration'
    ]

    process_steps = [
        {'step': 'Discovery', 'description': 'Understanding your requirements and goals'},
        {'step': 'Design', 'description': 'Creating wireframes and prototypes'},
        {'step': 'Development', 'description': 'Agile development with regular updates'},
        {'step': 'Testing', 'description': 'Quality assurance and user testing'},
        {'step': 'Deployment', 'description': 'Launch on app stores'},
        {'step': 'Support', 'description': 'Ongoing maintenance and updates'}
    ]

    return render_template('mobile_app.html',
                           title='Mobile App Development - GlobalTech&Trade',
                           active='it-solutions',
                           features=features,
                           process_steps=process_steps)


@app.route('/web-application-development')
def web_application_development():
    """Web application development page"""
    features = [
        'Frontend: React, Next.js, Vue.js',
        'Backend: Node.js, Python, PHP',
        'Database: PostgreSQL, MongoDB, MySQL',
        'Cloud: AWS, Azure, Google Cloud',
        'API Development & Integration',
        'E-commerce Solutions',
        'Content Management Systems',
        'Real-time Applications',
        'Progressive Web Apps',
        'Performance Optimization'
    ]

    return render_template('web_app.html',
                           title='Web App Development - GlobalTech&Trade',
                           active='it-solutions',
                           features=features)


@app.route('/graphic-design')
def graphic_design():
    """Graphic design services page"""
    services = [
        'Logo & Brand Identity',
        'UI/UX Design',
        'Marketing Materials',
        'Social Media Graphics',
        'Print Design',
        'Packaging Design',
        'Infographics',
        'Presentation Design'
    ]

    return render_template('graphic_design.html',
                           title='Graphic Design Services - GlobalTech&Trade',
                           active='it-solutions',
                           services=services)


# --- IMPORT/EXPORT ROUTES ---

@app.route('/import-export')
def import_export():
    """Import/Export overview page"""
    trade_routes = [
        {
            'route': 'India → Zambia',
            'origin': 'Mumbai, Chennai, Delhi',
            'destination': 'Lusaka, Ndola',
            'goods': 'Pharmaceuticals, Machinery, Textiles, Automotive Parts',
            'transit_time': '18-22 days',
            'efficiency': 96,
            'color': 'primary'
        },
        {
            'route': 'China → Zambia',
            'origin': 'Shanghai, Shenzhen, Guangzhou',
            'destination': 'Lusaka, Kitwe',
            'goods': 'Electronics, Solar Equipment, Consumer Goods, Machinery',
            'transit_time': '24-28 days',
            'efficiency': 92,
            'color': 'secondary'
        },
        {
            'route': 'Zambia → Global',
            'origin': 'Lusaka, Ndola',
            'destination': 'Worldwide',
            'goods': 'Copper, Minerals, Agricultural Products, Gemstones',
            'transit_time': 'Project based',
            'efficiency': 89,
            'color': 'accent'
        }
    ]

    services = [
        {
            'title': 'Customs Clearance',
            'description': 'Expert handling of all documentation and compliance requirements',
            'icon': 'file-contract',
            'color': 'primary'
        },
        {
            'title': 'Freight Forwarding',
            'description': 'Air, sea, and land freight solutions optimized for cost and time',
            'icon': 'truck',
            'color': 'secondary'
        },
        {
            'title': 'Sourcing & Procurement',
            'description': 'Direct sourcing from manufacturers with quality control',
            'icon': 'search',
            'color': 'accent'
        },
        {
            'title': 'Warehousing',
            'description': 'Secure storage facilities in strategic locations',
            'icon': 'warehouse',
            'color': 'primary'
        },
        {
            'title': 'Insurance',
            'description': 'Comprehensive cargo insurance coverage',
            'icon': 'shield-alt',
            'color': 'secondary'
        },
        {
            'title': 'Trade Consulting',
            'description': 'Market entry strategy and trade advisory',
            'icon': 'chart-line',
            'color': 'accent'
        }
    ]

    return render_template('import_export.html',
                           title='Import/Export Services - GlobalTech&Trade',
                           active='import-export',
                           trade_routes=trade_routes,
                           services=services)


# --- GENERAL SERVICES ROUTES ---

@app.route('/services')
def services():
    """All services hub page"""
    service_categories = [
        {
            'category': 'IT Solutions',
            'services': [
                {'name': 'Mobile Applications', 'url': '/mobile-app-development', 'icon': 'mobile-alt'},
                {'name': 'Web Applications', 'url': '/web-application-development', 'icon': 'globe'},
                {'name': 'Graphic Design', 'url': '/graphic-design', 'icon': 'paint-brush'}
            ]
        },
        {
            'category': 'Trade Services',
            'services': [
                {'name': 'Import/Export', 'url': '/import-export', 'icon': 'ship'},
                {'name': 'General Services & Supply', 'url': '/general-services', 'icon': 'truck'},
                {'name': 'Company Management', 'url': '/company-management', 'icon': 'building'}
            ]
        }
    ]

    return render_template('services.html',
                           title='All Services - GlobalTech&Trade',
                           active='services',
                           service_categories=service_categories)


@app.route('/company-management')
def company_management():
    """Company management services page"""
    services = [
        'Business Registration & Incorporation',
        'Tax Registration & Compliance',
        'Work Permits & Visas',
        'Company Secretarial Services',
        'Accounting & Bookkeeping',
        'Payroll Management',
        'Regulatory Compliance',
        'Annual Returns Filing',
        'Board Meeting Coordination',
        'Corporate Governance Advisory'
    ]

    benefits = [
        'Local expertise in both India and Zambia',
        'End-to-end compliance management',
        'Dedicated account manager',
        'Regular reporting and updates',
        'Competitive fixed fees'
    ]

    return render_template('company_management.html',
                           title='Company Management Services - GlobalTech&Trade',
                           active='services',
                           services=services,
                           benefits=benefits)


@app.route('/general-services')
def general_services():
    """General services and supply page"""
    services = [
        {
            'category': 'Procurement',
            'items': ['Industrial Equipment', 'Office Supplies', 'Raw Materials', 'Consumer Goods']
        },
        {
            'category': 'Logistics',
            'items': ['Transportation', 'Warehousing', 'Distribution', 'Inventory Management']
        },
        {
            'category': 'Supply Chain',
            'items': ['Supplier Sourcing', 'Quality Control', 'Order Processing', 'Last-mile Delivery']
        }
    ]

    return render_template('general_services.html',
                           title='General Services & Supply - GlobalTech&Trade',
                           active='services',
                           services=services)


# --- UTILITY ROUTES ---

@app.route('/subscribe', methods=['POST'])
def subscribe():
    """Newsletter subscription"""
    email = request.form.get('email', '').strip()

    if email and '@' in email and '.' in email:
        # Log subscription
        app.logger.info(f'Newsletter subscription: {email}')

        # Here you would typically add to email list
        flash('Successfully subscribed to our newsletter!', 'success')
    else:
        flash('Please enter a valid email address', 'error')

    return redirect(url_for('index'))


@app.route('/get-quote', methods=['POST'])
def get_quote():
    """Quick quote request"""
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    service = request.form.get('service', 'General')

    if name and email:
        app.logger.info(f'Quote request - Name: {name}, Email: {email}, Service: {service}')
        flash(f'Thank you {name}! We\'ll send your customized quote for {service} within 24 hours.', 'success')
    else:
        flash('Please provide your name and email', 'error')

    return redirect(url_for('index'))


@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    return {'status': 'healthy', 'timestamp': datetime.now().isoformat()}


@app.route('/sitemap.xml')
def sitemap():
    """Generate sitemap.xml"""
    pages = [
        {'loc': '/', 'lastmod': datetime.now().date().isoformat()},
        {'loc': '/about', 'lastmod': datetime.now().date().isoformat()},
        {'loc': '/services', 'lastmod': datetime.now().date().isoformat()},
        {'loc': '/it-solutions', 'lastmod': datetime.now().date().isoformat()},
        {'loc': '/mobile-app-development', 'lastmod': datetime.now().date().isoformat()},
        {'loc': '/web-application-development', 'lastmod': datetime.now().date().isoformat()},
        {'loc': '/graphic-design', 'lastmod': datetime.now().date().isoformat()},
        {'loc': '/import-export', 'lastmod': datetime.now().date().isoformat()},
        {'loc': '/company-management', 'lastmod': datetime.now().date().isoformat()},
        {'loc': '/general-services', 'lastmod': datetime.now().date().isoformat()},
        {'loc': '/contact', 'lastmod': datetime.now().date().isoformat()}
    ]

    sitemap_xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap_xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

    for page in pages:
        sitemap_xml += '  <url>\n'
        sitemap_xml += f'    <loc>http://localhost:5000{page["loc"]}</loc>\n'
        sitemap_xml += f'    <lastmod>{page["lastmod"]}</lastmod>\n'
        sitemap_xml += '    <changefreq>weekly</changefreq>\n'
        sitemap_xml += '    <priority>0.8</priority>\n'
        sitemap_xml += '  </url>\n'

    sitemap_xml += '</urlset>'

    return sitemap_xml, 200, {'Content-Type': 'application/xml'}


# Browser auto-open function
def open_browser():
    """Automatically open browser when server starts"""
    time.sleep(1.5)
    webbrowser.open_new("http://127.0.0.1:5000")


# Main entry point
if __name__ == '__main__':
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Auto-open browser in debug mode
    if app.debug and os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        threading.Thread(target=open_browser, daemon=True).start()
        print("🌐 Opening browser automatically...")

    print("=" * 60)
    print("🚀 GlobalTech&Trade Server Starting...")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print("📍 Local URL: http://localhost:5000")
    print("📍 Network URL: http://0.0.0.0:5000")
    print("=" * 60)
    print("📝 Press CTRL+C to stop the server")
    print("=" * 60)

    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)