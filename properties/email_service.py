import logging
import threading
from django.core.mail import EmailMultiAlternatives, get_connection
from django.conf import settings

logger = logging.getLogger(__name__)


def _send_notification_worker(inquiry):
    """
    Background worker that dispatches the inquiry email to the listing agent
    and the confirmation email to the client instantly.
    """
    try:
        property_obj = inquiry.property
        agent = getattr(property_obj, 'agent', None)

        agent_name = agent.name if agent else property_obj.agent_name
        agent_email = agent.email if agent else property_obj.agent_email
        agent_phone = agent.phone if agent else property_obj.agent_phone

        if not agent_email:
            logger.warning(f"No agent email found for property {property_obj.id}")
            return False

        client_name = inquiry.name
        client_email = inquiry.email
        client_phone = inquiry.phone or 'Not provided'
        inquiry_type = inquiry.inquiry_type or 'Schedule a Tour'
        client_message = inquiry.message or 'No additional notes provided.'

        property_title = property_obj.title
        property_price = getattr(property_obj, 'price_formatted', f"₹{property_obj.price:,.0f}")
        property_location = f"{property_obj.address}, {property_obj.city}, {property_obj.state}"
        property_url = f"http://localhost:5173/properties/{property_obj.id}"

        # ------------------------------------------------------------------
        # 1. Prepare Email to Listing Agent
        # ------------------------------------------------------------------
        agent_subject = f"🔔 New Client Inquiry: {inquiry_type} - {property_title}"

        agent_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="utf-8">
          <title>New Property Inquiry</title>
          <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #fafaf9; color: #1c1917; margin: 0; padding: 24px; }}
            .container {{ max-width: 600px; margin: 0 auto; background: #ffffff; border: 1px solid #e7e5e4; border-radius: 16px; overflow: hidden; }}
            .header {{ background: #1c1917; color: #fdfbf7; padding: 28px 24px; }}
            .header h1 {{ margin: 0; font-size: 22px; font-weight: normal; font-family: Georgia, serif; }}
            .header p {{ margin: 4px 0 0 0; font-size: 11px; text-transform: uppercase; letter-spacing: 0.18em; color: #a8a29e; }}
            .content {{ padding: 28px 24px; }}
            .badge {{ display: inline-block; padding: 4px 12px; background: #fef3c7; color: #92400e; border: 1px solid #fde68a; border-radius: 999px; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 16px; }}
            .property-box {{ background: #fbfbfa; border: 1px solid #e7e5e4; border-radius: 12px; padding: 16px; margin: 16px 0; }}
            .property-title {{ font-family: Georgia, serif; font-size: 17px; font-weight: normal; color: #0c0a09; margin: 0 0 4px 0; }}
            .property-sub {{ font-size: 12px; color: #78716c; margin: 0; }}
            .table {{ width: 100%; border-collapse: collapse; margin-top: 14px; font-size: 13px; }}
            .table td {{ padding: 8px 0; border-bottom: 1px solid #f5f5f4; }}
            .table td.label {{ color: #a8a29e; width: 35%; text-transform: uppercase; font-size: 10px; font-weight: 600; letter-spacing: 0.1em; }}
            .table td.val {{ color: #1c1917; font-weight: 500; }}
            .message-box {{ background: #fdfbf7; border-left: 3px solid #78350f; padding: 14px 16px; margin-top: 12px; font-size: 13px; color: #292524; font-style: italic; line-height: 1.6; border-radius: 0 8px 8px 0; }}
            .cta-btn {{ display: inline-block; background: #1c1917; color: #ffffff !important; text-decoration: none; padding: 12px 24px; border-radius: 10px; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.14em; margin-top: 20px; }}
            .footer {{ padding: 20px 24px; background: #fafaf9; border-top: 1px solid #f5f5f4; font-size: 11px; color: #a8a29e; text-align: center; }}
          </style>
        </head>
        <body>
          <div class="container">
            <div class="header">
              <p>Aura Luxury Estates • New Lead Notification</p>
              <h1>Client Inquiry for {agent_name}</h1>
            </div>
            <div class="content">
              <span class="badge">{inquiry_type}</span>
              <p style="font-size: 14px; margin: 0 0 12px 0;">Hello <strong>{agent_name}</strong>,</p>
              <p style="font-size: 13px; color: #57534e; margin: 0 0 16px 0; line-height: 1.5;">
                A prospective buyer/tenant has submitted an inquiry for your listing. You can simply <strong>hit Reply</strong> to contact the client directly at <strong>{client_email}</strong>.
              </p>

              <div class="property-box">
                <h2 class="property-title">{property_title}</h2>
                <p class="property-sub">{property_price} • {property_location}</p>
              </div>

              <h3 style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.15em; color: #78716c; margin: 20px 0 6px 0;">Client Contact Information</h3>
              <table class="table">
                <tr>
                  <td class="label">Full Name</td>
                  <td class="val"><strong>{client_name}</strong></td>
                </tr>
                <tr>
                  <td class="label">Email Address</td>
                  <td class="val"><a href="mailto:{client_email}" style="color: #92400e; text-decoration: none;">{client_email}</a></td>
                </tr>
                <tr>
                  <td class="label">Phone Number</td>
                  <td class="val"><a href="tel:{client_phone}" style="color: #1c1917; text-decoration: none;">{client_phone}</a></td>
                </tr>
                <tr>
                  <td class="label">Inquiry Type</td>
                  <td class="val">{inquiry_type}</td>
                </tr>
              </table>

              <h3 style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.15em; color: #78716c; margin: 20px 0 6px 0;">Client Message</h3>
              <div class="message-box">
                "{client_message}"
              </div>

              <div style="text-align: center; margin-top: 14px;">
                <a href="{property_url}" class="cta-btn" target="_blank">Open Property Details &rarr;</a>
              </div>
            </div>
            <div class="footer">
              This lead was generated from Aura Real Estate platform.<br>
              Direct Agent recipient: {agent_email}
            </div>
          </div>
        </body>
        </html>
        """

        agent_plain = f"""
Hello {agent_name},

You have received a new inquiry for {property_title} ({property_price})!

CLIENT INFORMATION:
- Name: {client_name}
- Email: {client_email}
- Phone: {client_phone}
- Inquiry Type: {inquiry_type}

CLIENT MESSAGE:
"{client_message}"

PROPERTY DETAILS:
- Title: {property_title}
- Price: {property_price}
- Address: {property_location}
- Link: {property_url}

To reply directly to {client_name}, simply reply to this email or write to {client_email}.
        """.strip()

        from_email = settings.DEFAULT_FROM_EMAIL

        # Strictly send ONLY to the specific listing agent of this property
        agent_email_msg = EmailMultiAlternatives(
            subject=agent_subject,
            body=agent_plain,
            from_email=from_email,
            to=[agent_email],
            reply_to=[client_email],  # Allows agent to reply directly to the customer
        )
        agent_email_msg.attach_alternative(agent_html, "text/html")

        # ------------------------------------------------------------------
        # 2. Prepare Confirmation Email to Client (Proof of Sent Inquiry)
        # ------------------------------------------------------------------
        client_subject = f"✅ Inquiry Confirmation: {property_title} (Sent to {agent_name})"

        client_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="utf-8">
          <title>Inquiry Confirmation</title>
          <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #fafaf9; color: #1c1917; margin: 0; padding: 24px; }}
            .container {{ max-width: 600px; margin: 0 auto; background: #ffffff; border: 1px solid #e7e5e4; border-radius: 16px; overflow: hidden; }}
            .header {{ background: #1c1917; color: #fdfbf7; padding: 28px 24px; }}
            .header h1 {{ margin: 0; font-size: 22px; font-weight: normal; font-family: Georgia, serif; }}
            .header p {{ margin: 4px 0 0 0; font-size: 11px; text-transform: uppercase; letter-spacing: 0.18em; color: #a8a29e; }}
            .content {{ padding: 28px 24px; }}
            .badge {{ display: inline-block; padding: 4px 12px; background: #ecfdf5; color: #065f46; border: 1px solid #a7f3d0; border-radius: 999px; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 16px; }}
            .agent-box {{ background: #fdfbf7; border: 1px solid #fed7aa; border-radius: 12px; padding: 16px; margin: 16px 0; }}
            .property-box {{ background: #fbfbfa; border: 1px solid #e7e5e4; border-radius: 12px; padding: 16px; margin: 16px 0; }}
            .property-title {{ font-family: Georgia, serif; font-size: 17px; font-weight: normal; color: #0c0a09; margin: 0 0 4px 0; }}
            .property-sub {{ font-size: 12px; color: #78716c; margin: 0; }}
            .message-box {{ background: #fbfbfa; border-left: 3px solid #1c1917; padding: 14px 16px; margin-top: 12px; font-size: 13px; color: #292524; font-style: italic; line-height: 1.6; border-radius: 0 8px 8px 0; }}
            .cta-btn {{ display: inline-block; background: #1c1917; color: #ffffff !important; text-decoration: none; padding: 12px 24px; border-radius: 10px; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.14em; margin-top: 20px; }}
            .footer {{ padding: 20px 24px; background: #fafaf9; border-top: 1px solid #f5f5f4; font-size: 11px; color: #a8a29e; text-align: center; }}
          </style>
        </head>
        <body>
          <div class="container">
            <div class="header">
              <p>Aura Luxury Estates • Inquiry Receipt</p>
              <h1>Your Inquiry Was Sent to {agent_name}</h1>
            </div>
            <div class="content">
              <span class="badge">Delivered to Agent</span>
              <p style="font-size: 14px; margin: 0 0 12px 0;">Hello <strong>{client_name}</strong>,</p>
              <p style="font-size: 13px; color: #57534e; margin: 0 0 16px 0; line-height: 1.5;">
                This receipt confirms that your inquiry has been dispatched to listing agent <strong>{agent_name}</strong>.
              </p>

              <div class="agent-box">
                <h3 style="margin: 0 0 6px 0; font-size: 13px; font-weight: 600; color: #9a3412; text-transform: uppercase; letter-spacing: 0.05em;">Assigned Listing Agent</h3>
                <p style="margin: 0; font-size: 14px; color: #1c1917;"><strong>{agent_name}</strong></p>
                <p style="margin: 4px 0 0 0; font-size: 12px; color: #78716c;">
                  Email: <a href="mailto:{agent_email}" style="color: #9a3412; text-decoration: none; font-weight: 500;">{agent_email}</a> | Phone: {agent_phone}
                </p>
              </div>

              <div class="property-box">
                <h2 class="property-title">{property_title}</h2>
                <p class="property-sub">{property_price} • {property_location}</p>
              </div>

              <h3 style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.15em; color: #78716c; margin: 20px 0 6px 0;">Your Message Sent to Agent</h3>
              <div class="message-box">
                "{client_message}"
              </div>

              <div style="text-align: center; margin-top: 14px;">
                <a href="{property_url}" class="cta-btn" target="_blank">View Property Listing &rarr;</a>
              </div>
            </div>
            <div class="footer">
              Aura Real Estate • Luxury Residential Portfolio<br>
              Direct Agent recipient: {agent_email}
            </div>
          </div>
        </body>
        </html>
        """

        client_plain = f"""
Hello {client_name},

This email confirms that your inquiry has been successfully delivered to listing agent {agent_name} ({agent_email}).

PROPERTY:
- Title: {property_title}
- Price: {property_price}
- Address: {property_location}
- Link: {property_url}

YOUR MESSAGE SENT TO {agent_name}:
"{client_message}"

LISTING AGENT CONTACT:
- Name: {agent_name}
- Email: {agent_email}
- Phone: {agent_phone}

{agent_name} will review your message and contact you directly.
        """.strip()

        client_email_msg = EmailMultiAlternatives(
            subject=client_subject,
            body=client_plain,
            from_email=from_email,
            to=[client_email],
            reply_to=[agent_email],
        )
        client_email_msg.attach_alternative(client_html, "text/html")

        # ------------------------------------------------------------------
        # 3. Dispatch to Agent & Client
        # ------------------------------------------------------------------
        if not settings.EMAIL_HOST_USER:
            # Direct cloud delivery to the assigned agent's inbox
            try:
                import urllib.request, json, ssl
                ctx = ssl._create_unverified_context()
                url = f"https://formsubmit.co/ajax/{agent_email}"
                payload = {
                    "_subject": f"🔔 [Client Inquiry] {inquiry_type} - {property_title}",
                    "Client Name": client_name,
                    "Client Email": client_email,
                    "Client Phone": client_phone,
                    "Inquiry Type": inquiry_type,
                    "Customer Message": client_message,
                    "Property Title": property_title,
                    "Price": property_price,
                    "Location": property_location,
                    "Listing URL": property_url,
                    "_template": "table"
                }
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode('utf-8'),
                    headers={
                        'Content-Type': 'application/json',
                        'Accept': 'application/json',
                        'Origin': 'http://localhost:5173',
                        'Referer': 'http://localhost:5173',
                        'User-Agent': 'Mozilla/5.0 (Aura Real Estate)'
                    }
                )
                with urllib.request.urlopen(req, context=ctx, timeout=8) as resp:
                    res_data = json.loads(resp.read().decode('utf-8'))
                    logger.info(f"Direct agent delivery status for {agent_email}: {res_data}")
            except Exception as e:
                logger.warning(f"Direct cloud dispatch notice: {e}")

        # Send via standard Django mail connection to both agent and client
        connection = get_connection(fail_silently=False)
        connection.open()
        try:
            connection.send_messages([agent_email_msg, client_email_msg])
            logger.info(f"Inquiry sent to agent {agent_email} and confirmation sent to client {client_email}")
            return True
        finally:
            connection.close()

    except Exception as exc:
        logger.error(f"Error in background email dispatch: {exc}", exc_info=True)
        return False


def send_inquiry_notification(inquiry, async_mode=True):
    """
    Triggers inquiry notification. Dispatches asynchronously via a background
    thread so the user's HTTP request completes instantly with zero lag.
    """
    if async_mode:
        thread = threading.Thread(
            target=_send_notification_worker,
            args=(inquiry,),
            daemon=True,
            name=f"InquiryEmailThread-{inquiry.id}"
        )
        thread.start()
        return True
    else:
        return _send_notification_worker(inquiry)
