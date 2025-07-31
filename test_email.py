"""
Test Email Functionality for Swing Sage
NUKE 28: Send Me My Swing Report - Email Testing
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email_config import EMAIL_CONFIG, test_email_config

def test_email_sending():
    """Test sending an email with PDF attachment"""
    
    # First check configuration
    if not test_email_config():
        return False
    
    try:
        # Create test message
        msg = MIMEMultipart()
        msg['From'] = f"{EMAIL_CONFIG['FROM_NAME']} <{EMAIL_CONFIG['FROM_EMAIL']}>"
        msg['To'] = 'test@example.com'  # Change to your test email
        msg['Subject'] = 'Swing Sage Test Email'
        
        # Email body
        body = """
        Hi there!
        
        This is a test email from Swing Sage to verify email functionality.
        
        If you receive this email, the email configuration is working correctly!
        
        Best regards,
        The Swing Sage Team
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Create a test PDF attachment
        test_pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 12 Tf\n72 720 Td\n(Test PDF) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000204 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n297\n%%EOF\n"
        
        # Attach test PDF
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(test_pdf_content)
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            'attachment; filename=test_report.pdf'
        )
        msg.attach(part)
        
        # Send email
        print("📧 Sending test email...")
        server = smtplib.SMTP(EMAIL_CONFIG['SMTP_SERVER'], EMAIL_CONFIG['SMTP_PORT'])
        server.starttls()
        server.login(EMAIL_CONFIG['USERNAME'], EMAIL_CONFIG['PASSWORD'])
        text = msg.as_string()
        server.sendmail(EMAIL_CONFIG['FROM_EMAIL'], 'test@example.com', text)
        server.quit()
        
        print("✅ Test email sent successfully!")
        print("📧 Check your email inbox for the test message.")
        return True
        
    except Exception as e:
        print(f"❌ Email test failed: {str(e)}")
        print("\n🔧 Troubleshooting:")
        print("1. Verify your Gmail app password is correct")
        print("2. Ensure 2-factor authentication is enabled")
        print("3. Check that the email address is correct")
        print("4. Verify network connectivity")
        return False

if __name__ == "__main__":
    print("🧪 Testing Swing Sage Email Functionality")
    print("=" * 50)
    test_email_sending() 