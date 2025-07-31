"""
Production Email Configuration for Swing Sage
NUKE 28: Send Me My Swing Report - Email Setup
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Email Configuration
EMAIL_CONFIG = {
    'SMTP_SERVER': 'smtp.gmail.com',
    'SMTP_PORT': 587,
    'USERNAME': os.getenv('SWING_SAGE_EMAIL', 'swing-sage@example.com'),
    'PASSWORD': os.getenv('SWING_SAGE_EMAIL_PASSWORD', 'your-app-password'),
    'FROM_NAME': 'Swing Sage',
    'FROM_EMAIL': os.getenv('SWING_SAGE_EMAIL', 'swing-sage@example.com')
}

# Gmail App Password Setup Instructions
GMAIL_SETUP_INSTRUCTIONS = """
🔧 Gmail App Password Setup for Swing Sage

To enable email functionality (NUKE 28), follow these steps:

1. Enable 2-Factor Authentication on your Gmail account
2. Generate an App Password:
   - Go to Google Account settings
   - Security > 2-Step Verification > App passwords
   - Select "Mail" and "Other (Custom name)"
   - Name it "Swing Sage"
   - Copy the generated 16-character password

3. Set Environment Variables:
   - Create a .env file in your project root
   - Add these lines:
     SWING_SAGE_EMAIL=your-email@gmail.com
     SWING_SAGE_EMAIL_PASSWORD=your-16-char-app-password

4. Test the configuration:
   python test_email.py

✅ Once configured, users can receive PDF reports via email!
"""

def test_email_config():
    """Test email configuration"""
    print("🧪 Testing Email Configuration...")
    
    if EMAIL_CONFIG['USERNAME'] == 'swing-sage@example.com':
        print("❌ Email not configured. Please set up environment variables.")
        print(GMAIL_SETUP_INSTRUCTIONS)
        return False
    
    if EMAIL_CONFIG['PASSWORD'] == 'your-app-password':
        print("❌ Email password not configured. Please set up app password.")
        print(GMAIL_SETUP_INSTRUCTIONS)
        return False
    
    print("✅ Email configuration appears to be set up correctly!")
    print(f"SMTP Server: {EMAIL_CONFIG['SMTP_SERVER']}:{EMAIL_CONFIG['SMTP_PORT']}")
    print(f"Username: {EMAIL_CONFIG['USERNAME']}")
    print(f"From: {EMAIL_CONFIG['FROM_NAME']} <{EMAIL_CONFIG['FROM_EMAIL']}>")
    return True

if __name__ == "__main__":
    test_email_config() 