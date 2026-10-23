from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings


class Command(BaseCommand):
    help = 'Test the email configuration by sending a verification email to a recipient'

    def add_arguments(self, parser):
        parser.add_argument('recipient', type=str, help='Email address to receive the test email')

    def handle(self, *args, **options):
        recipient = options['recipient']
        self.stdout.write(self.style.NOTICE(f"=== Django Email Configuration Test ==="))
        self.stdout.write(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
        self.stdout.write(f"EMAIL_HOST:    {settings.EMAIL_HOST}:{settings.EMAIL_PORT} (TLS={settings.EMAIL_USE_TLS})")
        self.stdout.write(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER or '(Not set - using console output)'}")
        self.stdout.write(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
        self.stdout.write(f"Sending test email to: {recipient}...")

        try:
            sent_count = send_mail(
                subject='[Test] Aura Real Estate Email Delivery Test',
                message=(
                    'Hello,\n\n'
                    'This is a verification email from Aura Luxury Real Estate.\n'
                    'Your email delivery pipeline is working successfully!\n\n'
                    'Agent inquiry emails will be delivered directly to this inbox.'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient],
                fail_silently=False,
            )
            if sent_count > 0:
                self.stdout.write(self.style.SUCCESS(f"SUCCESS: Email successfully sent to {recipient}!"))
            else:
                self.stdout.write(self.style.WARNING("WARNING: send_mail returned 0."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"ERROR: Failed to send email: {e}"))
            self.stdout.write(self.style.NOTICE(
                "\nTip for Gmail: Ensure you are using a 16-character App Password (not your normal password).\n"
                "Generate one at: https://myaccount.google.com/apppasswords"
            ))
