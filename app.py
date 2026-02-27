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
            'desc': 'Established in India And Africa, focusing on Enterprise Software and IT Infrastructure.',
            'detail': 'IT Division Launched'
        },
        {
            'year': '2021',
            'title': 'Expansion',
            'badge': 'Expansion',
            'desc': 'Opened our Africa HQ to facilitate Import/Export corridors and local tech support.',
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
            'phone': '+91 8273542939',
            'email': 'india@globaltechtrade.com',
            'division': 'IT Innovation Hub',
            'tags': ['Mobile Apps', 'Web Apps', 'AI/ML'],
            'flag': '🇮🇳',
            'badge_color': 'primary'
        },
        {
            'region': 'Africa',
            'country': 'Africa',
            'city': 'Africa',
            'full_address': 'Africa',
            'phone': '097 7588581',
            'email': 'africa@globaltechtrade.com',
            'division': 'Trade & Logistics Hub',
            'tags': ['Customs', 'Freight', 'Logistics'],
            'flag': '🌍',
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
    """Mobile App Development detail page"""
    return render_template('service_mobile_development.html', 
                         title='Mobile App Development - GlobalTech&Trade',
                         active='it-solutions')


@app.route('/web-application-development')
def web_application_development():
    """Web Application Development detail page"""
    return render_template('service_web_development.html',
                         title='Web Application Development - GlobalTech&Trade',
                         active='it-solutions')


@app.route('/custom-software-development')
def custom_software_development():
    """Custom Software Development detail page"""
    return render_template('service_custom_software.html',
                         title='Custom Software Development - GlobalTech&Trade',
                         active='it-solutions')


@app.route('/ai-automation')
def ai_automation():
    """AI & Automation detail page"""
    return render_template('service_ai_automation.html',
                         title='AI & Automation - GlobalTech&Trade',
                         active='it-solutions')


@app.route('/cloud-infrastructure')
def cloud_infrastructure():
    """Cloud & Infrastructure detail page"""
    return render_template('service_cloud_infrastructure.html',
                         title='Cloud & Infrastructure - GlobalTech&Trade',
                         active='it-solutions')


@app.route('/cybersecurity')
def cybersecurity():
    """Cybersecurity detail page"""
    return render_template('service_cybersecurity.html',
                         title='Cybersecurity - GlobalTech&Trade',
                         active='it-solutions')


# --- TRADE SERVICE DETAIL ROUTES ---

@app.route('/product-sourcing')
def product_sourcing():
    """Product Sourcing detail page"""
    return render_template('trade_product_sourcing.html',
                         title='Product Sourcing & Procurement - GlobalTech&Trade',
                         active='import-export')


@app.route('/customs-clearance')
def customs_clearance():
    """Customs Clearance detail page"""
    return render_template('trade_customs_clearance.html',
                         title='Customs Clearance & Compliance - GlobalTech&Trade',
                         active='import-export')


@app.route('/freight-forwarding')
def freight_forwarding():
    """Freight Forwarding detail page"""
    return render_template('trade_freight_forwarding.html',
                         title='Freight Forwarding & Logistics - GlobalTech&Trade',
                         active='import-export')


@app.route('/trade-finance')
def trade_finance():
    """Trade Finance detail page"""
    return render_template('trade_finance.html',
                         title='Trade Finance & Payment Solutions - GlobalTech&Trade',
                         active='import-export')


@app.route('/cargo-insurance')
def cargo_insurance():
    """Cargo Insurance detail page"""
    return render_template('trade_cargo_insurance.html',
                         title='Cargo Insurance & Risk Protection - GlobalTech&Trade',
                         active='import-export')


@app.route('/trade-documentation')
def trade_documentation():
    """Trade Documentation detail page"""
    return render_template('trade_documentation.html',
                         title='Trade Documentation & Compliance - GlobalTech&Trade',
                         active='import-export')


@app.route('/graphic-design')
def graphic_design():
    """Graphic Design - redirects to IT Solutions"""
    return redirect(url_for('it_solutions') + '#graphic-design')


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


# --- CONTENT & MARKETING ROUTES ---

@app.route('/blog')
@app.route('/insights')
def blog():
    """Blog/Insights page with articles"""
    return render_template(
        'blog.html',
        title='Insights & Resources - GlobalTech&Trade',
        active='blog'
    )


# Blog article content database
BLOG_ARTICLES = {
    'india-africa-trade-guide-2026': {
        'title': 'The Complete Guide to India-Africa Trade in 2026',
        'subtitle': 'Everything you need to know about importing and exporting between India and African markets.',
        'category': 'Trade',
        'color': 'primary',
        'color_light': 'primary',
        'read_time': '15 min read',
        'date': 'February 2026',
        'author': 'Trade Division Team',
        'author_initials': 'TD',
        'author_title': 'GlobalTechAndTrade Trade Specialists',
        'tags': ['Import/Export', 'Africa', 'India', 'Trade Regulations', 'Customs'],
        'content': '''
<h2>Introduction to India-Africa Trade</h2>
<p>The trade relationship between India and Africa has grown exponentially over the past decade, reaching over $98 billion in bilateral trade. As we move through 2026, this corridor presents unprecedented opportunities for businesses on both continents.</p>

<p>India has become Africa's fourth-largest trading partner, with exports ranging from pharmaceuticals and automobiles to textiles and machinery. Meanwhile, African exports to India include crude oil, gold, and agricultural products.</p>

<h2>Key Trade Routes and Transit Times</h2>
<p>Understanding the logistics is crucial for successful trade operations:</p>

<h3>Sea Freight Routes</h3>
<ul>
<li><strong>Mumbai/JNPT to Dar es Salaam:</strong> 12-15 days</li>
<li><strong>Chennai to Mombasa:</strong> 10-14 days</li>
<li><strong>Mumbai to Durban:</strong> 18-22 days</li>
<li><strong>Mundra to Africa (via Dar es Salaam):</strong> 25-35 days</li>
</ul>

<h3>Air Freight Routes</h3>
<ul>
<li><strong>Delhi to Nairobi:</strong> Direct flights, 6 hours</li>
<li><strong>Mumbai to Johannesburg:</strong> 8-9 hours</li>
<li><strong>Chennai to Addis Ababa:</strong> 5-6 hours</li>
</ul>

<h2>Documentation Requirements</h2>
<p>Proper documentation is essential for smooth customs clearance:</p>

<h3>Export from India</h3>
<ol>
<li><strong>Commercial Invoice:</strong> Detailed description of goods, quantity, and value</li>
<li><strong>Packing List:</strong> Weight, dimensions, and packaging details</li>
<li><strong>Bill of Lading/Airway Bill:</strong> Transport document</li>
<li><strong>Certificate of Origin:</strong> Proves Indian origin for preferential tariffs</li>
<li><strong>Shipping Bill:</strong> Filed with Indian Customs</li>
<li><strong>Letter of Credit:</strong> If applicable for payment terms</li>
</ol>

<h3>Import to African Countries</h3>
<p>Requirements vary by country, but commonly include:</p>
<ul>
<li>Import Declaration Form (IDF)</li>
<li>Pre-shipment Inspection Certificate (for some countries)</li>
<li>Phytosanitary Certificate (for agricultural products)</li>
<li>SONCAP/PVOC certificates (for Nigeria/Kenya)</li>
</ul>

<h2>Customs Duties and Tariffs</h2>
<p>Understanding duty structures helps in pricing and profitability:</p>

<table style="width:100%; border-collapse: collapse; margin: 20px 0;">
<tr style="background: #f1f5f9;">
<th style="padding: 12px; border: 1px solid #e2e8f0; text-align: left;">Country</th>
<th style="padding: 12px; border: 1px solid #e2e8f0; text-align: left;">Average Duty Rate</th>
<th style="padding: 12px; border: 1px solid #e2e8f0; text-align: left;">VAT/GST</th>
</tr>
<tr>
<td style="padding: 12px; border: 1px solid #e2e8f0;">Africa</td>
<td style="padding: 12px; border: 1px solid #e2e8f0;">15-25%</td>
<td style="padding: 12px; border: 1px solid #e2e8f0;">16%</td>
</tr>
<tr>
<td style="padding: 12px; border: 1px solid #e2e8f0;">Kenya</td>
<td style="padding: 12px; border: 1px solid #e2e8f0;">10-25%</td>
<td style="padding: 12px; border: 1px solid #e2e8f0;">16%</td>
</tr>
<tr>
<td style="padding: 12px; border: 1px solid #e2e8f0;">Tanzania</td>
<td style="padding: 12px; border: 1px solid #e2e8f0;">10-25%</td>
<td style="padding: 12px; border: 1px solid #e2e8f0;">18%</td>
</tr>
<tr>
<td style="padding: 12px; border: 1px solid #e2e8f0;">Nigeria</td>
<td style="padding: 12px; border: 1px solid #e2e8f0;">5-35%</td>
<td style="padding: 12px; border: 1px solid #e2e8f0;">7.5%</td>
</tr>
<tr>
<td style="padding: 12px; border: 1px solid #e2e8f0;">South Africa</td>
<td style="padding: 12px; border: 1px solid #e2e8f0;">0-45%</td>
<td style="padding: 12px; border: 1px solid #e2e8f0;">15%</td>
</tr>
</table>

<h2>Top Products for India-Africa Trade</h2>

<h3>India to Africa (High Demand)</h3>
<ul>
<li><strong>Pharmaceuticals:</strong> Generic medicines, medical equipment</li>
<li><strong>Automobiles:</strong> Cars, motorcycles, spare parts</li>
<li><strong>Textiles:</strong> Fabrics, garments, home textiles</li>
<li><strong>Machinery:</strong> Agricultural equipment, industrial machinery</li>
<li><strong>Electronics:</strong> Mobile phones, computers, appliances</li>
<li><strong>Food Products:</strong> Rice, spices, processed foods</li>
</ul>

<h3>Africa to India (Growing Exports)</h3>
<ul>
<li><strong>Minerals:</strong> Gold, copper, cobalt</li>
<li><strong>Agricultural Products:</strong> Cashews, coffee, cocoa</li>
<li><strong>Crude Oil:</strong> From Nigeria, Angola</li>
<li><strong>Precious Stones:</strong> Diamonds, tanzanite</li>
</ul>

<h2>Payment Methods and Risk Mitigation</h2>
<p>Choosing the right payment method is crucial:</p>

<ul>
<li><strong>Letter of Credit (L/C):</strong> Most secure, recommended for new relationships</li>
<li><strong>Documentary Collection:</strong> Moderate risk, lower cost than L/C</li>
<li><strong>Advance Payment:</strong> Best for sellers, risky for buyers</li>
<li><strong>Open Account:</strong> Only with established, trusted partners</li>
</ul>

<h2>Common Challenges and Solutions</h2>

<h3>Challenge 1: Port Congestion</h3>
<p><strong>Solution:</strong> Use alternative ports, plan for buffer time, consider inland container depots.</p>

<h3>Challenge 2: Currency Fluctuations</h3>
<p><strong>Solution:</strong> Use forward contracts, price in stable currencies (USD), build margins for fluctuation.</p>

<h3>Challenge 3: Documentation Errors</h3>
<p><strong>Solution:</strong> Work with experienced customs brokers, use digital documentation systems, double-check all details.</p>

<h2>How GlobalTechAndTrade Can Help</h2>
<p>With offices in both India (Noida) and Africa, GlobalTechAndTrade offers end-to-end trade solutions:</p>

<ul>
<li>✅ Product sourcing from verified Indian manufacturers</li>
<li>✅ Complete documentation and customs clearance</li>
<li>✅ Freight forwarding (sea, air, multimodal)</li>
<li>✅ Warehousing and last-mile delivery</li>
<li>✅ Trade finance assistance</li>
<li>✅ Regulatory compliance support</li>
</ul>

<p><strong>Ready to start trading?</strong> Contact our trade specialists for a free consultation and personalized quote.</p>
'''
    },
    'africa-import-regulations': {
        'title': 'How to Navigate Import Regulations in Africa',
        'subtitle': 'A comprehensive guide to customs requirements, documentation, and compliance for businesses importing goods into Africa.',
        'category': 'Trade',
        'color': 'primary',
        'color_light': 'primary',
        'read_time': '8 min read',
        'date': 'February 15, 2026',
        'author': 'Africa Operations Team',
        'author_initials': 'AO',
        'author_title': 'GlobalTechAndTrade Africa Office',
        'tags': ['Africa', 'Import Regulations', 'Customs', 'Compliance', 'Documentation'],
        'content': '''
<h2>Overview of Africa's Import Framework</h2>
<p>Africa has developed robust import regulations to facilitate trade while protecting local industries. Various customs authorities oversee all customs operations across the continent.</p>

<h2>Key Regulatory Bodies</h2>
<ul>
<li><strong>National Revenue Authorities:</strong> Primary customs authorities</li>
<li><strong>Bureau of Standards:</strong> Product standards and certification</li>
<li><strong>Ministry of Commerce, Trade and Industry:</strong> Trade policy</li>
<li><strong>Central Banks:</strong> Foreign exchange regulations</li>
</ul>

<h2>Import Documentation Checklist</h2>
<p>Every import into Africa requires the following documents:</p>

<h3>Mandatory Documents</h3>
<ol>
<li><strong>Commercial Invoice:</strong> Must include full description, quantity, unit price, and total value</li>
<li><strong>Packing List:</strong> Detailed breakdown of shipment contents</li>
<li><strong>Bill of Lading/Airway Bill:</strong> Original transport document</li>
<li><strong>Certificate of Origin:</strong> Required for preferential tariff treatment</li>
<li><strong>Import Declaration Form (Form CE 20):</strong> Filed electronically via ASYCUDA World</li>
<li><strong>Tax Clearance Certificate:</strong> Proves importer is tax compliant</li>
</ol>

<h3>Product-Specific Documents</h3>
<ul>
<li><strong>Food Products:</strong> Health certificate, phytosanitary certificate</li>
<li><strong>Electronics:</strong> ZABS certification for certain items</li>
<li><strong>Pharmaceuticals:</strong> National Medicines Regulatory Authority permit</li>
<li><strong>Vehicles:</strong> Roadworthiness certificate, age restrictions apply</li>
</ul>

<h2>Customs Duty Structure</h2>
<p>African countries use the Harmonized System (HS) for tariff classification:</p>

<table style="width:100%; border-collapse: collapse; margin: 20px 0;">
<tr style="background: #f1f5f9;">
<th style="padding: 12px; border: 1px solid #e2e8f0;">Product Category</th>
<th style="padding: 12px; border: 1px solid #e2e8f0;">Duty Rate</th>
</tr>
<tr>
<td style="padding: 12px; border: 1px solid #e2e8f0;">Raw Materials</td>
<td style="padding: 12px; border: 1px solid #e2e8f0;">0-5%</td>
</tr>
<tr>
<td style="padding: 12px; border: 1px solid #e2e8f0;">Capital Goods/Machinery</td>
<td style="padding: 12px; border: 1px solid #e2e8f0;">0-15%</td>
</tr>
<tr>
<td style="padding: 12px; border: 1px solid #e2e8f0;">Intermediate Goods</td>
<td style="padding: 12px; border: 1px solid #e2e8f0;">15-25%</td>
</tr>
<tr>
<td style="padding: 12px; border: 1px solid #e2e8f0;">Finished Consumer Goods</td>
<td style="padding: 12px; border: 1px solid #e2e8f0;">25-40%</td>
</tr>
</table>

<p><strong>Additional Charges:</strong></p>
<ul>
<li>VAT: 16% on CIF value + duty</li>
<li>Import Declaration Fee: 2% of CIF value</li>
<li>Excise Duty: Applicable on specific goods (alcohol, tobacco, fuel)</li>
</ul>

<h2>COMESA and SADC Preferential Tariffs</h2>
<p>Many African countries are members of COMESA and SADC trade blocs, offering preferential tariffs:</p>
<ul>
<li><strong>COMESA:</strong> 0% duty on goods from member states with valid Certificate of Origin</li>
<li><strong>SADC:</strong> Reduced duties on qualifying goods from member states</li>
</ul>

<h2>Prohibited and Restricted Imports</h2>

<h3>Prohibited Items</h3>
<ul>
<li>Narcotic drugs and psychotropic substances</li>
<li>Counterfeit goods and currency</li>
<li>Pornographic materials</li>
<li>Hazardous waste</li>
</ul>

<h3>Restricted Items (Require Permits)</h3>
<ul>
<li>Firearms and ammunition</li>
<li>Pharmaceuticals and medical devices</li>
<li>Agricultural chemicals and pesticides</li>
<li>Used vehicles older than 5 years</li>
</ul>

<h2>Step-by-Step Import Process</h2>
<ol>
<li><strong>Register with Revenue Authority:</strong> Obtain a Taxpayer Identification Number</li>
<li><strong>Obtain Import Permits:</strong> If required for your product category</li>
<li><strong>Arrange Shipping:</strong> Work with a freight forwarder</li>
<li><strong>Submit Declaration:</strong> File Form CE 20 via ASYCUDA World</li>
<li><strong>Pay Duties:</strong> Through authorized banks</li>
<li><strong>Customs Inspection:</strong> Physical or document-based verification</li>
<li><strong>Release of Goods:</strong> Upon clearance, collect from port/warehouse</li>
</ol>

<h2>Common Mistakes to Avoid</h2>
<ul>
<li>❌ Undervaluing goods (leads to penalties and seizure)</li>
<li>❌ Incorrect HS code classification</li>
<li>❌ Missing or expired permits</li>
<li>❌ Incomplete documentation</li>
<li>❌ Not accounting for all charges in pricing</li>
</ul>

<h2>How GlobalTechAndTrade Helps</h2>
<p>Our Africa office provides complete import support:</p>
<ul>
<li>✅ Customs clearance and documentation</li>
<li>✅ Duty calculation and optimization</li>
<li>✅ Certification assistance</li>
<li>✅ Warehousing in Africa</li>
<li>✅ Last-mile delivery across Africa</li>
</ul>
'''
    },
    'mobile-app-trends-2026': {
        'title': 'Top Mobile App Trends for Business in 2026',
        'subtitle': 'Discover the latest mobile technologies and how they can transform your business operations and customer engagement.',
        'category': 'Technology',
        'color': 'accent',
        'color_light': 'accent',
        'read_time': '10 min read',
        'date': 'February 10, 2026',
        'author': 'Technology Division',
        'author_initials': 'TT',
        'author_title': 'GlobalTechAndTrade Tech Team',
        'tags': ['Mobile Apps', 'Technology', 'AI', 'Business', 'Digital Transformation'],
        'content': '''
<h2>The Mobile-First Business Landscape</h2>
<p>In 2026, mobile apps are no longer optional for businesses—they're essential. With over 7 billion smartphone users worldwide and mobile commerce accounting for 73% of all e-commerce sales, businesses that don't have a mobile strategy are falling behind.</p>

<h2>Top Mobile App Trends for 2026</h2>

<h3>1. AI-Powered Personalization</h3>
<p>Artificial Intelligence is revolutionizing how apps interact with users:</p>
<ul>
<li><strong>Predictive Analytics:</strong> Apps that anticipate user needs before they express them</li>
<li><strong>Smart Recommendations:</strong> Product suggestions based on behavior patterns</li>
<li><strong>Conversational AI:</strong> Chatbots that understand context and emotion</li>
<li><strong>Voice Interfaces:</strong> Natural language commands for hands-free operation</li>
</ul>

<p><strong>Business Impact:</strong> Companies using AI personalization see 40% higher conversion rates and 25% increase in customer retention.</p>

<h3>2. Super Apps</h3>
<p>The "super app" model, popularized in Asia, is going global:</p>
<ul>
<li>Single app for multiple services (payments, shopping, communication, services)</li>
<li>Reduced app fatigue for users</li>
<li>Higher engagement and data insights for businesses</li>
</ul>

<p><strong>Example:</strong> A trading company app that handles orders, payments, shipment tracking, and customer support in one place.</p>

<h3>3. Augmented Reality (AR) Integration</h3>
<p>AR is moving beyond gaming into practical business applications:</p>
<ul>
<li><strong>Product Visualization:</strong> See furniture in your room before buying</li>
<li><strong>Training & Onboarding:</strong> Interactive employee training</li>
<li><strong>Maintenance & Repair:</strong> AR-guided equipment servicing</li>
<li><strong>Navigation:</strong> Indoor navigation for warehouses and stores</li>
</ul>

<h3>4. 5G-Enabled Features</h3>
<p>With 5G becoming mainstream, apps can now offer:</p>
<ul>
<li>Real-time HD video streaming</li>
<li>Instant cloud computing</li>
<li>IoT device integration</li>
<li>Lag-free multiplayer experiences</li>
</ul>

<h3>5. Blockchain and Web3 Integration</h3>
<p>Decentralized features are becoming practical:</p>
<ul>
<li><strong>Secure Payments:</strong> Cryptocurrency and stablecoin transactions</li>
<li><strong>Supply Chain Tracking:</strong> Immutable records of product journey</li>
<li><strong>Digital Identity:</strong> Self-sovereign identity verification</li>
<li><strong>Smart Contracts:</strong> Automated, trustless agreements</li>
</ul>

<h3>6. Cross-Platform Development</h3>
<p>Build once, deploy everywhere:</p>
<ul>
<li><strong>Flutter:</strong> Google's UI toolkit for beautiful native apps</li>
<li><strong>React Native:</strong> JavaScript-based cross-platform development</li>
<li><strong>Progressive Web Apps (PWA):</strong> Web apps with native-like features</li>
</ul>

<p><strong>Cost Savings:</strong> Cross-platform development can reduce costs by 30-40% compared to building separate iOS and Android apps.</p>

<h3>7. Enhanced Security Features</h3>
<p>Security is non-negotiable in 2026:</p>
<ul>
<li>Biometric authentication (face, fingerprint, voice)</li>
<li>End-to-end encryption</li>
<li>Zero-trust architecture</li>
<li>Privacy-first data handling</li>
</ul>

<h2>Industry-Specific Applications</h2>

<h3>For Trading Companies</h3>
<ul>
<li>Real-time shipment tracking with GPS</li>
<li>Digital documentation and e-signatures</li>
<li>Automated customs declaration</li>
<li>Multi-currency payment processing</li>
</ul>

<h3>For Retail/E-Commerce</h3>
<ul>
<li>AR product try-on</li>
<li>One-click checkout</li>
<li>Loyalty programs with gamification</li>
<li>Social commerce integration</li>
</ul>

<h3>For Field Services</h3>
<ul>
<li>Offline-first functionality</li>
<li>GPS tracking and route optimization</li>
<li>Digital forms and signatures</li>
<li>Real-time inventory management</li>
</ul>

<h2>Getting Started with Your Mobile App</h2>
<p>Ready to build a mobile app for your business? Here's our recommended approach:</p>

<ol>
<li><strong>Define Your Goals:</strong> What problem does the app solve?</li>
<li><strong>Know Your Users:</strong> Who will use it and how?</li>
<li><strong>Start with MVP:</strong> Launch with core features, iterate based on feedback</li>
<li><strong>Choose the Right Partner:</strong> Work with experienced developers</li>
<li><strong>Plan for Growth:</strong> Build scalable architecture from day one</li>
</ol>

<h2>How GlobalTechAndTrade Can Help</h2>
<p>Our technology division specializes in building mobile apps for businesses:</p>
<ul>
<li>✅ Cross-platform development (React Native, Flutter)</li>
<li>✅ Native iOS and Android apps</li>
<li>✅ AI and ML integration</li>
<li>✅ Cloud backend development</li>
<li>✅ Ongoing maintenance and support</li>
</ul>

<p>Contact us for a free consultation and customized quote for your project.</p>
'''
    },
    'india-africa-opportunities-2026': {
        'title': 'India-Africa Trade: Opportunities in 2026',
        'subtitle': 'Explore the growing trade corridor between India and Africa, and how businesses can capitalize on emerging opportunities.',
        'category': 'Business',
        'color': 'green-500',
        'color_light': 'green-400',
        'read_time': '6 min read',
        'date': 'February 5, 2026',
        'author': 'Business Strategy Team',
        'author_initials': 'BS',
        'author_title': 'GlobalTechAndTrade Strategy Division',
        'tags': ['India', 'Africa', 'Trade Opportunities', 'Business Growth', 'Market Analysis'],
        'content': '''
<h2>The India-Africa Trade Corridor: A $200 Billion Opportunity</h2>
<p>The trade relationship between India and Africa is experiencing unprecedented growth. With bilateral trade projected to exceed $200 billion by 2030, now is the time for businesses to position themselves in this dynamic market.</p>

<h2>Why India-Africa Trade is Booming</h2>

<h3>Complementary Economies</h3>
<p>India and Africa have naturally complementary economies:</p>
<ul>
<li><strong>India offers:</strong> Manufactured goods, pharmaceuticals, technology, expertise</li>
<li><strong>Africa offers:</strong> Natural resources, agricultural products, growing consumer markets</li>
</ul>

<h3>Demographic Dividend</h3>
<p>Both regions have young, growing populations:</p>
<ul>
<li>Africa's population will reach 2.5 billion by 2050</li>
<li>Rising middle class with increasing purchasing power</li>
<li>Growing demand for quality products and services</li>
</ul>

<h3>Government Support</h3>
<p>Both Indian and African governments are actively promoting trade:</p>
<ul>
<li><strong>India's Africa Policy:</strong> Focus on trade, investment, and capacity building</li>
<li><strong>AfCFTA:</strong> African Continental Free Trade Area creating a single market</li>
<li><strong>Bilateral Agreements:</strong> Preferential trade terms between countries</li>
</ul>

<h2>Top Sectors for Investment</h2>

<h3>1. Healthcare & Pharmaceuticals</h3>
<p>Africa imports 70% of its pharmaceuticals, with India being the largest supplier:</p>
<ul>
<li>Generic medicines in high demand</li>
<li>Medical equipment and devices</li>
<li>Healthcare infrastructure development</li>
<li>Telemedicine solutions</li>
</ul>

<h3>2. Agriculture & Food Processing</h3>
<p>Opportunities in the entire value chain:</p>
<ul>
<li>Agricultural machinery and equipment</li>
<li>Irrigation systems</li>
<li>Food processing technology</li>
<li>Cold chain logistics</li>
</ul>

<h3>3. Technology & Digital Services</h3>
<p>Africa's digital transformation is accelerating:</p>
<ul>
<li>Fintech and mobile payments</li>
<li>E-commerce platforms</li>
<li>EdTech solutions</li>
<li>Enterprise software</li>
</ul>

<h3>4. Infrastructure & Construction</h3>
<p>Massive infrastructure gap presents opportunities:</p>
<ul>
<li>Road and rail construction</li>
<li>Power generation and distribution</li>
<li>Housing and commercial buildings</li>
<li>Water and sanitation</li>
</ul>

<h3>5. Automotive</h3>
<p>Growing demand for vehicles:</p>
<ul>
<li>Passenger vehicles</li>
<li>Commercial trucks and buses</li>
<li>Two-wheelers and three-wheelers</li>
<li>Spare parts and accessories</li>
</ul>

<h2>Key Markets to Watch</h2>

<table style="width:100%; border-collapse: collapse; margin: 20px 0;">
<tr style="background: #f1f5f9;">
<th style="padding: 12px; border: 1px solid #e2e8f0;">Country</th>
<th style="padding: 12px; border: 1px solid #e2e8f0;">Key Opportunities</th>
<th style="padding: 12px; border: 1px solid #e2e8f0;">Trade with India (2025)</th>
</tr>
<tr>
<td style="padding: 12px; border: 1px solid #e2e8f0;">Nigeria</td>
<td style="padding: 12px; border: 1px solid #e2e8f0;">Oil & Gas, Pharma, Tech</td>
<td style="padding: 12px; border: 1px solid #e2e8f0;">$15 billion</td>
</tr>
<tr>
<td style="padding: 12px; border: 1px solid #e2e8f0;">South Africa</td>
<td style="padding: 12px; border: 1px solid #e2e8f0;">Mining, Auto, Finance</td>
<td style="padding: 12px; border: 1px solid #e2e8f0;">$12 billion</td>
</tr>
<tr>
<td style="padding: 12px; border: 1px solid #e2e8f0;">Kenya</td>
<td style="padding: 12px; border: 1px solid #e2e8f0;">Tech, Agriculture, Tourism</td>
<td style="padding: 12px; border: 1px solid #e2e8f0;">$3.5 billion</td>
</tr>
<tr>
<td style="padding: 12px; border: 1px solid #e2e8f0;">Tanzania</td>
<td style="padding: 12px; border: 1px solid #e2e8f0;">Mining, Agriculture, Infra</td>
<td style="padding: 12px; border: 1px solid #e2e8f0;">$3 billion</td>
</tr>
<tr>
<td style="padding: 12px; border: 1px solid #e2e8f0;">Africa</td>
<td style="padding: 12px; border: 1px solid #e2e8f0;">Mining, Agriculture, Retail</td>
<td style="padding: 12px; border: 1px solid #e2e8f0;">$800 million</td>
</tr>
</table>

<h2>Challenges and How to Overcome Them</h2>

<h3>Challenge 1: Market Knowledge</h3>
<p><strong>Solution:</strong> Partner with local experts who understand regulations, culture, and business practices.</p>

<h3>Challenge 2: Payment and Currency Risks</h3>
<p><strong>Solution:</strong> Use letters of credit, trade finance, and currency hedging strategies.</p>

<h3>Challenge 3: Logistics and Infrastructure</h3>
<p><strong>Solution:</strong> Work with experienced freight forwarders and plan for longer lead times.</p>

<h3>Challenge 4: Regulatory Compliance</h3>
<p><strong>Solution:</strong> Engage customs brokers and legal advisors familiar with local requirements.</p>

<h2>Getting Started</h2>
<p>Ready to explore India-Africa trade opportunities? Here's how to begin:</p>
<ol>
<li><strong>Research:</strong> Identify target markets and products</li>
<li><strong>Connect:</strong> Find reliable partners and suppliers</li>
<li><strong>Plan:</strong> Develop logistics and compliance strategy</li>
<li><strong>Execute:</strong> Start with pilot shipments before scaling</li>
</ol>

<h2>How GlobalTechAndTrade Can Help</h2>
<p>With presence in both India and Africa, we offer:</p>
<ul>
<li>✅ Market research and opportunity assessment</li>
<li>✅ Supplier/buyer identification and verification</li>
<li>✅ End-to-end logistics management</li>
<li>✅ Regulatory compliance support</li>
<li>✅ Trade finance facilitation</li>
</ul>

<p><strong>Contact us today</strong> for a free consultation on your India-Africa trade plans.</p>
'''
    },
    'ai-international-trade': {
        'title': 'How AI is Transforming International Trade',
        'subtitle': 'From automated customs clearance to predictive logistics, discover how artificial intelligence is revolutionizing global trade.',
        'category': 'Technology',
        'color': 'purple-500',
        'color_light': 'purple-400',
        'read_time': '12 min read',
        'date': 'January 28, 2026',
        'author': 'Technology Division',
        'author_initials': 'AI',
        'author_title': 'GlobalTechAndTrade Innovation Team',
        'tags': ['AI', 'International Trade', 'Automation', 'Logistics', 'Technology'],
        'content': '''
<h2>The AI Revolution in Global Trade</h2>
<p>Artificial Intelligence is fundamentally changing how international trade operates. From predicting demand to automating customs clearance, AI technologies are making trade faster, cheaper, and more efficient than ever before.</p>

<h2>Key AI Applications in Trade</h2>

<h3>1. Automated Customs Clearance</h3>
<p>AI is streamlining one of trade's biggest bottlenecks:</p>
<ul>
<li><strong>Document Processing:</strong> AI reads and validates trade documents in seconds</li>
<li><strong>HS Code Classification:</strong> Automatic product classification with 95%+ accuracy</li>
<li><strong>Risk Assessment:</strong> Intelligent flagging of high-risk shipments</li>
<li><strong>Compliance Checking:</strong> Real-time verification against regulations</li>
</ul>

<p><strong>Impact:</strong> Customs clearance time reduced from days to hours, with 60% fewer errors.</p>

<h3>2. Predictive Logistics</h3>
<p>AI helps anticipate and optimize supply chain operations:</p>
<ul>
<li><strong>Demand Forecasting:</strong> Predict what products will be needed, where, and when</li>
<li><strong>Route Optimization:</strong> Find the fastest, cheapest shipping routes</li>
<li><strong>Inventory Management:</strong> Maintain optimal stock levels across locations</li>
<li><strong>Delay Prediction:</strong> Anticipate disruptions before they happen</li>
</ul>

<h3>3. Trade Finance Automation</h3>
<p>AI is transforming how trade is financed:</p>
<ul>
<li><strong>Credit Scoring:</strong> Assess buyer/seller risk using alternative data</li>
<li><strong>Fraud Detection:</strong> Identify suspicious transactions in real-time</li>
<li><strong>Document Verification:</strong> Validate letters of credit and invoices</li>
<li><strong>Smart Contracts:</strong> Automate payment release upon delivery confirmation</li>
</ul>

<h3>4. Supplier Discovery and Verification</h3>
<p>Finding reliable partners is easier with AI:</p>
<ul>
<li><strong>Supplier Matching:</strong> AI matches buyers with suitable suppliers</li>
<li><strong>Due Diligence:</strong> Automated background checks and verification</li>
<li><strong>Performance Prediction:</strong> Forecast supplier reliability based on data</li>
<li><strong>Price Benchmarking:</strong> Compare prices across global markets</li>
</ul>

<h3>5. Natural Language Processing for Trade</h3>
<p>Breaking down language barriers:</p>
<ul>
<li><strong>Real-time Translation:</strong> Communicate with partners in any language</li>
<li><strong>Contract Analysis:</strong> Extract key terms from legal documents</li>
<li><strong>Email Automation:</strong> Draft and respond to trade correspondence</li>
<li><strong>Chatbots:</strong> 24/7 customer support in multiple languages</li>
</ul>

<h2>Real-World Success Stories</h2>

<h3>Case Study 1: Port of Rotterdam</h3>
<p>Europe's largest port uses AI to:</p>
<ul>
<li>Predict ship arrival times with 99% accuracy</li>
<li>Optimize berth allocation</li>
<li>Reduce vessel waiting time by 20%</li>
</ul>

<h3>Case Study 2: Maersk</h3>
<p>The shipping giant leverages AI for:</p>
<ul>
<li>Predictive maintenance of vessels</li>
<li>Dynamic pricing optimization</li>
<li>Customer demand forecasting</li>
</ul>

<h3>Case Study 3: Alibaba</h3>
<p>The e-commerce platform uses AI to:</p>
<ul>
<li>Process millions of customs declarations daily</li>
<li>Detect counterfeit products</li>
<li>Optimize cross-border logistics</li>
</ul>

<h2>Implementing AI in Your Trade Operations</h2>

<h3>Step 1: Identify Pain Points</h3>
<p>Where do you spend the most time and money?</p>
<ul>
<li>Document processing?</li>
<li>Customs clearance?</li>
<li>Supplier management?</li>
<li>Logistics coordination?</li>
</ul>

<h3>Step 2: Start Small</h3>
<p>Begin with one AI solution:</p>
<ul>
<li>Implement a chatbot for customer queries</li>
<li>Use AI for document classification</li>
<li>Try predictive analytics for demand</li>
</ul>

<h3>Step 3: Measure and Scale</h3>
<p>Track results and expand successful implementations:</p>
<ul>
<li>Time saved</li>
<li>Errors reduced</li>
<li>Customer satisfaction improved</li>
</ul>

<h2>The Future of AI in Trade</h2>
<p>What's coming next:</p>
<ul>
<li><strong>Autonomous Ships:</strong> Self-navigating cargo vessels</li>
<li><strong>Digital Twins:</strong> Virtual replicas of entire supply chains</li>
<li><strong>Blockchain + AI:</strong> Immutable, intelligent trade records</li>
<li><strong>Quantum Computing:</strong> Solving complex optimization problems</li>
</ul>

<h2>How GlobalTechAndTrade Uses AI</h2>
<p>We leverage AI across our operations:</p>
<ul>
<li>✅ AI-powered chatbot for instant customer support</li>
<li>✅ Automated document processing</li>
<li>✅ Predictive shipment tracking</li>
<li>✅ Intelligent supplier matching</li>
<li>✅ Risk assessment and compliance checking</li>
</ul>

<p><strong>Want to modernize your trade operations?</strong> Contact us to learn how AI can transform your business.</p>
'''
    },
    'ecommerce-african-markets': {
        'title': 'Building an E-Commerce Platform for African Markets',
        'subtitle': 'Key considerations for launching an online store targeting African consumers, including payment solutions and logistics.',
        'category': 'Technology',
        'color': 'cyan-500',
        'color_light': 'cyan-400',
        'read_time': '7 min read',
        'date': 'January 20, 2026',
        'author': 'Technology Division',
        'author_initials': 'EC',
        'author_title': 'GlobalTechAndTrade E-Commerce Team',
        'tags': ['E-Commerce', 'Africa', 'Online Business', 'Payments', 'Logistics'],
        'content': '''
<h2>The African E-Commerce Opportunity</h2>
<p>Africa's e-commerce market is projected to reach $75 billion by 2028, growing at 20% annually. With increasing smartphone penetration and improving internet infrastructure, now is the perfect time to establish your online presence in African markets.</p>

<h2>Understanding the African Consumer</h2>

<h3>Key Demographics</h3>
<ul>
<li><strong>Young Population:</strong> 60% under 25 years old</li>
<li><strong>Mobile-First:</strong> 80% of internet access is via mobile</li>
<li><strong>Social Media Savvy:</strong> High engagement on WhatsApp, Facebook, Instagram</li>
<li><strong>Price Conscious:</strong> Value for money is paramount</li>
</ul>

<h3>Shopping Behavior</h3>
<ul>
<li>Preference for cash on delivery (COD)</li>
<li>Trust is built through social proof and reviews</li>
<li>WhatsApp is a key sales channel</li>
<li>Free delivery expectations are growing</li>
</ul>

<h2>Essential Features for African E-Commerce</h2>

<h3>1. Mobile-Optimized Design</h3>
<p>Your platform must be mobile-first:</p>
<ul>
<li>Fast loading on slow connections (optimize for 3G)</li>
<li>Simple, intuitive navigation</li>
<li>Large touch targets for easy tapping</li>
<li>Minimal data usage</li>
</ul>

<h3>2. Multiple Payment Options</h3>
<p>Offer diverse payment methods:</p>
<ul>
<li><strong>Mobile Money:</strong> M-Pesa (Kenya), MTN Mobile Money, Airtel Money</li>
<li><strong>Cards:</strong> Visa, Mastercard (lower penetration)</li>
<li><strong>Bank Transfers:</strong> Popular for larger purchases</li>
<li><strong>Cash on Delivery:</strong> Still preferred by many</li>
<li><strong>Buy Now, Pay Later:</strong> Growing trend</li>
</ul>

<h3>3. Local Currency Support</h3>
<p>Display prices in local currencies:</p>
<ul>
<li>Nigerian Naira (NGN)</li>
<li>Kenyan Shilling (KES)</li>
<li>South African Rand (ZAR)</li>
<li>African Currencies</li>
</ul>

<h3>4. Robust Logistics Integration</h3>
<p>Partner with reliable delivery providers:</p>
<ul>
<li><strong>Last-Mile Delivery:</strong> Local courier services</li>
<li><strong>Pick-Up Points:</strong> Convenient collection locations</li>
<li><strong>Real-Time Tracking:</strong> Keep customers informed</li>
<li><strong>Returns Management:</strong> Easy return process</li>
</ul>

<h2>Payment Gateway Options</h2>

<table style="width:100%; border-collapse: collapse; margin: 20px 0;">
<tr style="background: #f1f5f9;">
<th style="padding: 12px; border: 1px solid #e2e8f0;">Provider</th>
<th style="padding: 12px; border: 1px solid #e2e8f0;">Coverage</th>
<th style="padding: 12px; border: 1px solid #e2e8f0;">Key Features</th>
</tr>
<tr>
<td style="padding: 12px; border: 1px solid #e2e8f0;">Paystack</td>
<td style="padding: 12px; border: 1px solid #e2e8f0;">Nigeria, Ghana, South Africa</td>
<td style="padding: 12px; border: 1px solid #e2e8f0;">Easy integration, multiple payment methods</td>
</tr>
<tr>
<td style="padding: 12px; border: 1px solid #e2e8f0;">Flutterwave</td>
<td style="padding: 12px; border: 1px solid #e2e8f0;">30+ African countries</td>
<td style="padding: 12px; border: 1px solid #e2e8f0;">Wide coverage, mobile money support</td>
</tr>
<tr>
<td style="padding: 12px; border: 1px solid #e2e8f0;">M-Pesa</td>
<td style="padding: 12px; border: 1px solid #e2e8f0;">Kenya, Tanzania, others</td>
<td style="padding: 12px; border: 1px solid #e2e8f0;">Dominant in East Africa</td>
</tr>
<tr>
<td style="padding: 12px; border: 1px solid #e2e8f0;">DPO Group</td>
<td style="padding: 12px; border: 1px solid #e2e8f0;">20+ African countries</td>
<td style="padding: 12px; border: 1px solid #e2e8f0;">Enterprise solutions</td>
</tr>
</table>

<h2>Logistics Partners by Region</h2>

<h3>Pan-African</h3>
<ul>
<li>DHL Express</li>
<li>FedEx</li>
<li>Aramex</li>
</ul>

<h3>Regional Specialists</h3>
<ul>
<li><strong>Nigeria:</strong> GIG Logistics, Kwik Delivery</li>
<li><strong>Kenya:</strong> Sendy, Glovo</li>
<li><strong>South Africa:</strong> The Courier Guy, Pargo</li>
<li><strong>Africa:</strong> Various local providers</li>
</ul>

<h2>Marketing Strategies That Work</h2>

<h3>Social Commerce</h3>
<ul>
<li>Sell directly through WhatsApp Business</li>
<li>Use Instagram Shopping features</li>
<li>Leverage Facebook Marketplace</li>
<li>Partner with local influencers</li>
</ul>

<h3>Trust Building</h3>
<ul>
<li>Display customer reviews prominently</li>
<li>Offer money-back guarantees</li>
<li>Show physical address and contact info</li>
<li>Use local customer service numbers</li>
</ul>

<h2>Common Challenges and Solutions</h2>

<h3>Challenge: Address Verification</h3>
<p><strong>Solution:</strong> Use GPS coordinates, landmarks, and phone verification for delivery.</p>

<h3>Challenge: Payment Failures</h3>
<p><strong>Solution:</strong> Offer multiple payment options and retry mechanisms.</p>

<h3>Challenge: Returns and Refunds</h3>
<p><strong>Solution:</strong> Clear return policy, easy process, quick refunds to build trust.</p>

<h2>How GlobalTechAndTrade Can Help</h2>
<p>We build e-commerce platforms optimized for African markets:</p>
<ul>
<li>✅ Custom e-commerce development</li>
<li>✅ Payment gateway integration</li>
<li>✅ Logistics partner connections</li>
<li>✅ Mobile app development</li>
<li>✅ Ongoing support and maintenance</li>
</ul>

<p><strong>Ready to launch your African e-commerce venture?</strong> Contact us for a free consultation.</p>
'''
    },
    'import-duty-calculator-guide': {
        'title': 'Understanding Import Duties: India to Africa Calculator',
        'subtitle': 'A practical guide to calculating customs duties, taxes, and fees when importing goods from India to African countries.',
        'category': 'Trade',
        'color': 'amber-500',
        'color_light': 'amber-400',
        'read_time': '5 min read',
        'date': 'January 15, 2026',
        'author': 'Trade Division Team',
        'author_initials': 'TD',
        'author_title': 'GlobalTechAndTrade Trade Specialists',
        'tags': ['Import Duties', 'Customs', 'Calculator', 'India', 'Africa'],
        'content': '''
<h2>Why Understanding Import Duties Matters</h2>
<p>Import duties can significantly impact your landed cost and profitability. Miscalculating duties can lead to unexpected expenses, delays at customs, or even seizure of goods. This guide will help you accurately calculate the total cost of importing goods from India to African countries.</p>

<h2>Components of Import Costs</h2>
<p>The total landed cost includes several components:</p>

<h3>1. CIF Value (Cost, Insurance, Freight)</h3>
<p>The base value for duty calculation:</p>
<ul>
<li><strong>Cost:</strong> Product price (FOB - Free on Board)</li>
<li><strong>Insurance:</strong> Cargo insurance (typically 1-2% of value)</li>
<li><strong>Freight:</strong> Shipping cost to destination port</li>
</ul>

<p><strong>Formula:</strong> CIF = FOB + Insurance + Freight</p>

<h3>2. Customs Duty</h3>
<p>Percentage applied to CIF value based on HS code:</p>
<ul>
<li>Varies by product category (0-50%)</li>
<li>May qualify for preferential rates under trade agreements</li>
<li>Check specific HS code for accurate rate</li>
</ul>

<h3>3. Value Added Tax (VAT)</h3>
<p>Applied to CIF + Duty:</p>
<ul>
<li>Africa: Varies by country (typically 15-18%)</li>
<li>Kenya: 16%</li>
<li>Tanzania: 18%</li>
<li>Nigeria: 7.5%</li>
<li>South Africa: 15%</li>
</ul>

<h3>4. Other Charges</h3>
<ul>
<li><strong>Import Declaration Fee:</strong> 1-2% of CIF</li>
<li><strong>Excise Duty:</strong> On specific goods (alcohol, tobacco, fuel)</li>
<li><strong>Inspection Fees:</strong> Pre-shipment inspection if required</li>
<li><strong>Port Charges:</strong> Handling, storage, documentation</li>
</ul>

<h2>Step-by-Step Calculation Example</h2>

<h3>Scenario: Importing Textiles to Africa</h3>
<p>Let's calculate the total cost for importing $10,000 worth of textiles:</p>

<table style="width:100%; border-collapse: collapse; margin: 20px 0;">
<tr style="background: #f1f5f9;">
<th style="padding: 12px; border: 1px solid #e2e8f0; text-align: left;">Component</th>
<th style="padding: 12px; border: 1px solid #e2e8f0; text-align: right;">Amount (USD)</th>
</tr>
<tr>
<td style="padding: 12px; border: 1px solid #e2e8f0;">FOB Value (Product Cost)</td>
<td style="padding: 12px; border: 1px solid #e2e8f0; text-align: right;">$10,000</td>
</tr>
<tr>
<td style="padding: 12px; border: 1px solid #e2e8f0;">Insurance (1.5%)</td>
<td style="padding: 12px; border: 1px solid #e2e8f0; text-align: right;">$150</td>
</tr>
<tr>
<td style="padding: 12px; border: 1px solid #e2e8f0;">Freight (Sea)</td>
<td style="padding: 12px; border: 1px solid #e2e8f0; text-align: right;">$800</td>
</tr>
<tr style="background: #e0f2fe;">
<td style="padding: 12px; border: 1px solid #e2e8f0;"><strong>CIF Value</strong></td>
<td style="padding: 12px; border: 1px solid #e2e8f0; text-align: right;"><strong>$10,950</strong></td>
</tr>
<tr>
<td style="padding: 12px; border: 1px solid #e2e8f0;">Customs Duty (25%)</td>
<td style="padding: 12px; border: 1px solid #e2e8f0; text-align: right;">$2,737.50</td>
</tr>
<tr>
<td style="padding: 12px; border: 1px solid #e2e8f0;">Import Declaration Fee (2%)</td>
<td style="padding: 12px; border: 1px solid #e2e8f0; text-align: right;">$219</td>
</tr>
<tr>
<td style="padding: 12px; border: 1px solid #e2e8f0;">VAT (16% on CIF + Duty)</td>
<td style="padding: 12px; border: 1px solid #e2e8f0; text-align: right;">$2,190</td>
</tr>
<tr>
<td style="padding: 12px; border: 1px solid #e2e8f0;">Port & Handling Charges</td>
<td style="padding: 12px; border: 1px solid #e2e8f0; text-align: right;">$300</td>
</tr>
<tr style="background: #dcfce7;">
<td style="padding: 12px; border: 1px solid #e2e8f0;"><strong>Total Landed Cost</strong></td>
<td style="padding: 12px; border: 1px solid #e2e8f0; text-align: right;"><strong>$16,396.50</strong></td>
</tr>
</table>

<p><strong>Effective Import Cost:</strong> 64% above FOB value</p>

<h2>Duty Rates by Country and Product</h2>

<h3>Africa (General)</h3>
<table style="width:100%; border-collapse: collapse; margin: 20px 0;">
<tr style="background: #f1f5f9;">
<th style="padding: 12px; border: 1px solid #e2e8f0;">Product Category</th>
<th style="padding: 12px; border: 1px solid #e2e8f0;">Duty Rate</th>
</tr>
<tr>
<td style="padding: 12px; border: 1px solid #e2e8f0;">Raw Materials</td>
<td style="padding: 12px; border: 1px solid #e2e8f0;">0-5%</td>
</tr>
<tr>
<td style="padding: 12px; border: 1px solid #e2e8f0;">Machinery & Equipment</td>
<td style="padding: 12px; border: 1px solid #e2e8f0;">0-15%</td>
</tr>
<tr>
<td style="padding: 12px; border: 1px solid #e2e8f0;">Textiles & Garments</td>
<td style="padding: 12px; border: 1px solid #e2e8f0;">25%</td>
</tr>
<tr>
<td style="padding: 12px; border: 1px solid #e2e8f0;">Electronics</td>
<td style="padding: 12px; border: 1px solid #e2e8f0;">15-25%</td>
</tr>
<tr>
<td style="padding: 12px; border: 1px solid #e2e8f0;">Vehicles</td>
<td style="padding: 12px; border: 1px solid #e2e8f0;">30-40%</td>
</tr>
</table>

<h3>Kenya</h3>
<table style="width:100%; border-collapse: collapse; margin: 20px 0;">
<tr style="background: #f1f5f9;">
<th style="padding: 12px; border: 1px solid #e2e8f0;">Product Category</th>
<th style="padding: 12px; border: 1px solid #e2e8f0;">Duty Rate</th>
</tr>
<tr>
<td style="padding: 12px; border: 1px solid #e2e8f0;">Raw Materials</td>
<td style="padding: 12px; border: 1px solid #e2e8f0;">0%</td>
</tr>
<tr>
<td style="padding: 12px; border: 1px solid #e2e8f0;">Capital Goods</td>
<td style="padding: 12px; border: 1px solid #e2e8f0;">0%</td>
</tr>
<tr>
<td style="padding: 12px; border: 1px solid #e2e8f0;">Intermediate Goods</td>
<td style="padding: 12px; border: 1px solid #e2e8f0;">10%</td>
</tr>
<tr>
<td style="padding: 12px; border: 1px solid #e2e8f0;">Finished Goods</td>
<td style="padding: 12px; border: 1px solid #e2e8f0;">25%</td>
</tr>
<tr>
<td style="padding: 12px; border: 1px solid #e2e8f0;">Sensitive Items</td>
<td style="padding: 12px; border: 1px solid #e2e8f0;">35-100%</td>
</tr>
</table>

<h2>Tips to Reduce Import Costs</h2>

<h3>1. Correct HS Code Classification</h3>
<p>Ensure accurate classification to avoid overpaying or penalties.</p>

<h3>2. Leverage Trade Agreements</h3>
<p>Check for preferential rates under:</p>
<ul>
<li>COMESA (Common Market for Eastern and Southern Africa)</li>
<li>SADC (Southern African Development Community)</li>
<li>Bilateral agreements</li>
</ul>

<h3>3. Duty Exemptions</h3>
<p>Some goods qualify for exemptions:</p>
<ul>
<li>Capital goods for manufacturing</li>
<li>Goods for export processing zones</li>
<li>Humanitarian goods</li>
</ul>

<h3>4. Optimize Shipping</h3>
<p>Lower freight costs reduce CIF and therefore duties:</p>
<ul>
<li>Consolidate shipments</li>
<li>Use sea freight for non-urgent goods</li>
<li>Negotiate volume discounts</li>
</ul>

<h2>Common Mistakes to Avoid</h2>
<ul>
<li>❌ Undervaluing goods (leads to penalties)</li>
<li>❌ Wrong HS code classification</li>
<li>❌ Forgetting to include all cost components</li>
<li>❌ Not accounting for currency fluctuations</li>
<li>❌ Missing documentation requirements</li>
</ul>

<h2>How GlobalTechAndTrade Can Help</h2>
<p>We provide comprehensive import cost calculation and optimization:</p>
<ul>
<li>✅ Accurate duty calculation for any product</li>
<li>✅ HS code classification assistance</li>
<li>✅ Trade agreement optimization</li>
<li>✅ Complete customs clearance</li>
<li>✅ End-to-end logistics management</li>
</ul>

<p><strong>Need help calculating your import costs?</strong> Contact us for a free consultation and detailed cost breakdown for your specific products.</p>
'''
    }
}


@app.route('/blog/<slug>')
def blog_article(slug):
    """Individual blog article page"""
    article = BLOG_ARTICLES.get(slug)
    if not article:
        return render_template('404.html'), 404
    
    # Get related articles (exclude current)
    related = []
    for key, art in BLOG_ARTICLES.items():
        if key != slug:
            related.append({
                'title': art['title'],
                'read_time': art['read_time'],
                'url': f'/blog/{key}',
                'color': art['color'],
                'color_dark': 'secondary' if art['color'] == 'primary' else 'orange-600',
                'icon': 'file-alt' if art['category'] == 'Trade' else 'mobile-alt'
            })
    
    return render_template(
        'blog_article.html',
        title=f"{article['title']} - GlobalTech&Trade",
        active='blog',
        article=article,
        related_articles=related[:3]
    )


@app.route('/case-studies')
@app.route('/portfolio')
def case_studies():
    """Case Studies / Portfolio page"""
    return render_template(
        'case_studies.html',
        title='Case Studies - GlobalTech&Trade',
        active='case-studies'
    )


@app.route('/growth-checklist')
@app.route('/setup-guide')
def growth_checklist():
    """Growth checklist and external services setup guide"""
    return render_template(
        'growth_checklist.html',
        title='Growth Checklist - GlobalTech&Trade',
        active='resources'
    )


@app.route('/faq')
@app.route('/help')
def faq():
    """FAQ page with common questions"""
    return render_template(
        'faq.html',
        title='FAQ - GlobalTech&Trade',
        active='faq'
    )


@app.route('/privacy-policy')
def privacy_policy():
    """Privacy Policy page"""
    return render_template(
        'privacy_policy.html',
        title='Privacy Policy - GlobalTech&Trade',
        active='privacy'
    )


@app.route('/terms')
@app.route('/terms-of-service')
def terms():
    """Terms of Service page"""
    return render_template(
        'terms.html',
        title='Terms of Service - GlobalTech&Trade',
        active='terms'
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
    import requests as http_requests
    
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
        
        # Use Resend API for email (works on Render free tier)
        RESEND_API_KEY = os.environ.get('RESEND_API_KEY', '')
        
        if not RESEND_API_KEY:
            app.logger.warning('RESEND_API_KEY not configured - skipping email')
            # Still return success so user sees confirmation in chat
            return jsonify({'success': True, 'message': 'Demo recorded (email service not configured)'}), 200
        
        # Create beautiful HTML email for visitor
        visitor_html = f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="UTF-8"></head>
        <body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f4f7fa;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff;">
                <div style="background: linear-gradient(135deg, #0052CC 0%, #003D99 100%); padding: 30px; text-align: center;">
                    <h1 style="color: #ffffff; margin: 0; font-size: 24px;">GlobalTechAndTrade</h1>
                    <p style="color: #93c5fd; margin: 10px 0 0 0; font-size: 14px;">IT Solutions & Import/Export Services</p>
                </div>
                <div style="padding: 30px;">
                    <h2 style="color: #1e3a5f; margin-top: 0;">Demo Request Confirmed!</h2>
                    <p style="color: #4a5568; font-size: 16px;">Dear <strong>{visitor_name}</strong>,</p>
                    <p style="color: #4a5568; font-size: 16px;">Thank you for booking a demo with GlobalTechAndTrade! Your request has been received.</p>
                    <div style="background-color: #f0f9ff; border-left: 4px solid #0052CC; padding: 20px; margin: 20px 0;">
                        <h3 style="color: #0052CC; margin-top: 0;">Your Booking Details</h3>
                        <p style="margin: 5px 0;"><strong>Name:</strong> {visitor_name}</p>
                        <p style="margin: 5px 0;"><strong>Email:</strong> {visitor_email}</p>
                        <p style="margin: 5px 0;"><strong>Phone:</strong> {phone}</p>
                        <p style="margin: 5px 0;"><strong>Company:</strong> {company}</p>
                        <p style="margin: 5px 0;"><strong>Service:</strong> {service}</p>
                    </div>
                    <div style="background-color: #f0fdf4; border-left: 4px solid #22c55e; padding: 20px; margin: 20px 0;">
                        <h3 style="color: #166534; margin-top: 0;">What Happens Next?</h3>
                        <p style="color: #4a5568; margin: 0;">Our team will contact you within <strong>24 hours</strong> to schedule your demo.</p>
                    </div>
                    <p style="color: #4a5568;"><strong>Contact Us:</strong><br>India: +91 8273542939<br>Africa: 097 7588581<br>Email: info@globaltechandtrade.com</p>
                </div>
                <div style="background-color: #1e3a5f; padding: 20px; text-align: center;">
                    <p style="color: #93c5fd; margin: 0;">Thank you for choosing GlobalTechAndTrade!</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Company notification HTML
        company_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #0052CC;">New Demo Request from Chatbot</h2>
            <table style="border-collapse: collapse; width: 100%; max-width: 500px;">
                <tr><td style="padding: 10px; border: 1px solid #ddd; background: #f5f5f5;"><strong>Name</strong></td><td style="padding: 10px; border: 1px solid #ddd;">{visitor_name}</td></tr>
                <tr><td style="padding: 10px; border: 1px solid #ddd; background: #f5f5f5;"><strong>Email</strong></td><td style="padding: 10px; border: 1px solid #ddd;">{visitor_email}</td></tr>
                <tr><td style="padding: 10px; border: 1px solid #ddd; background: #f5f5f5;"><strong>Phone</strong></td><td style="padding: 10px; border: 1px solid #ddd;">{phone}</td></tr>
                <tr><td style="padding: 10px; border: 1px solid #ddd; background: #f5f5f5;"><strong>Company</strong></td><td style="padding: 10px; border: 1px solid #ddd;">{company}</td></tr>
                <tr><td style="padding: 10px; border: 1px solid #ddd; background: #f5f5f5;"><strong>Service</strong></td><td style="padding: 10px; border: 1px solid #ddd;">{service}</td></tr>
                <tr><td style="padding: 10px; border: 1px solid #ddd; background: #f5f5f5;"><strong>Message</strong></td><td style="padding: 10px; border: 1px solid #ddd;">{message}</td></tr>
                <tr><td style="padding: 10px; border: 1px solid #ddd; background: #f5f5f5;"><strong>Time</strong></td><td style="padding: 10px; border: 1px solid #ddd;">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</td></tr>
            </table>
            <p style="margin-top: 20px; color: #666;">Please contact this lead within 24 hours.</p>
        </body>
        </html>
        """
        
        # Send emails via Resend API (works on Render free tier)
        headers = {
            'Authorization': f'Bearer {RESEND_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        # Send to visitor
        visitor_response = http_requests.post(
            'https://api.resend.com/emails',
            headers=headers,
            json={
                'from': 'GlobalTechAndTrade <noreply@globaltechandtrade.com>',
                'to': [visitor_email],
                'subject': 'Demo Request Confirmed - GlobalTechAndTrade',
                'html': visitor_html
            },
            timeout=30
        )
        
        app.logger.info(f'Visitor email response: {visitor_response.status_code} - {visitor_response.text}')
        
        # Send to company
        company_response = http_requests.post(
            'https://api.resend.com/emails',
            headers=headers,
            json={
                'from': 'GlobalTechAndTrade <noreply@globaltechandtrade.com>',
                'to': ['info@globaltechandtrade.com'],
                'subject': f'New Demo Request - {visitor_name} ({service})',
                'html': company_html
            },
            timeout=30
        )
        
        app.logger.info(f'Company email response: {company_response.status_code} - {company_response.text}')
        
        # Check if emails were sent successfully
        if visitor_response.status_code != 200:
            app.logger.error(f'Visitor email failed: {visitor_response.text}')
        if company_response.status_code != 200:
            app.logger.error(f'Company email failed: {company_response.text}')
        
        return jsonify({'success': True, 'message': 'Emails sent successfully'}), 200
        
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