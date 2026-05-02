import os
import sys
import django
from django.core.mail import send_mail
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def send_test_email(recipient, subject="Kyusa Test Email", message="This is a test email from the Kyusa backend."):
    print(f"Attempting to send email...")
    print(f"From: {settings.DEFAULT_FROM_EMAIL}")
    print(f"To: {recipient}")
    print(f"SMTP Host: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            fail_silently=False,
        )
        print("\n✅ Success! Email sent successfully.")
    except Exception as e:
        print(f"\n❌ Error: Failed to send email.")
        print(f"Details: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_email.py <recipient_email> [subject] [message]")
        print("Example: python test_email.py user@example.com 'Hello' 'This is my message'")
        sys.exit(1)

    target_email = sys.argv[1]
    target_subject = sys.argv[2] if len(sys.argv) > 2 else "Kyusa Test Email"
    target_message = sys.argv[3] if len(sys.argv) > 3 else "This is a test email from the Kyusa backend."

    send_test_email(target_email, target_subject, target_message)
