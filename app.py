from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
from datetime import datetime, timedelta
import secrets
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
    PERMANENT_SESSION_LIFETIME=timedelta(days=7)
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
    return render_template('404.html', title='Page Not Found'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html', title='Server Error'), 500


# --- MAIN NAVIGATION ROUTES ---

@app.route('/')
def index():
    """Home page route"""
    # Featured services for the homepage hero section
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
    # Company history milestones
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

    # Office details
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

            # In a real app, you would send an email here using Flask-Mail
            # return redirect(url_for('contact'))

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
    # Core services for the grid
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

    # Trade Routes (India-Africa specific focus based on your new HTML)
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

    # Core Logistics Services
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
    # Categories for the services grid
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
    """Simple health check for monitoring"""
    return {'status': 'healthy', 'timestamp': datetime.now().isoformat()}


# --- MAIN ENTRY POINT ---

if __name__ == '__main__':
    # Create logs directory if not exists
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Determine port (Render vs Local)
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('PORT') is None  # Debug only if running locally

    print("=" * 60)
    print("🚀 GlobalTech&Trade Server Starting...")
    print("=" * 60)

    # Run app
    app.run(debug=debug_mode, host='0.0.0.0', port=port, threaded=True)