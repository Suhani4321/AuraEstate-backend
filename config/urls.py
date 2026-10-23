from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse, HttpResponse

def home_view(request):
    if 'application/json' in request.META.get('HTTP_ACCEPT', ''):
        return JsonResponse({
            "status": "online",
            "message": "AuraEstate Backend API is running successfully!",
            "database": "Neon PostgreSQL",
            "endpoints": {
                "admin": "/admin/",
                "properties": "/api/properties/",
                "featured": "/api/properties/featured/",
                "agents": "/api/agents/",
            }
        })

    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AuraEstate Backend Status</title>
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
        <style>
            * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Plus Jakarta Sans', sans-serif; }
            body {
                background: radial-gradient(circle at 50% 20%, #151d2f 0%, #0a0e17 100%);
                color: #f1f5f9;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 24px;
            }
            .card {
                background: rgba(255, 255, 255, 0.04);
                backdrop-filter: blur(16px);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 20px;
                padding: 40px;
                max-width: 520px;
                width: 100%;
                box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
                text-align: center;
            }
            .badge {
                display: inline-flex;
                align-items: center;
                gap: 8px;
                background: rgba(16, 185, 129, 0.12);
                color: #34d399;
                padding: 8px 16px;
                border-radius: 9999px;
                font-size: 13px;
                font-weight: 600;
                margin-bottom: 24px;
                border: 1px solid rgba(52, 211, 153, 0.25);
            }
            .pulse {
                width: 8px;
                height: 8px;
                background: #34d399;
                border-radius: 50%;
                box-shadow: 0 0 0 0 rgba(52, 211, 153, 0.7);
                animation: pulse 2s infinite;
            }
            @keyframes pulse {
                0% { box-shadow: 0 0 0 0 rgba(52, 211, 153, 0.7); }
                70% { box-shadow: 0 0 0 8px rgba(52, 211, 153, 0); }
                100% { box-shadow: 0 0 0 0 rgba(52, 211, 153, 0); }
            }
            h1 { font-size: 26px; font-weight: 700; margin-bottom: 10px; color: #ffffff; }
            p { color: #94a3b8; font-size: 14px; line-height: 1.6; margin-bottom: 30px; }
            .links { display: flex; flex-direction: column; gap: 12px; }
            .btn {
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 14px 20px;
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 12px;
                color: #e2e8f0;
                text-decoration: none;
                font-size: 14px;
                font-weight: 500;
                transition: all 0.2s ease;
            }
            .btn:hover {
                background: rgba(255, 255, 255, 0.1);
                border-color: rgba(255, 255, 255, 0.2);
                transform: translateY(-2px);
            }
            .tag {
                font-size: 11px;
                background: rgba(99, 102, 241, 0.2);
                color: #a5b4fc;
                padding: 4px 8px;
                border-radius: 6px;
                font-family: monospace;
            }
        </style>
    </head>
    <body>
        <div class="card">
            <div class="badge">
                <span class="pulse"></span>
                Backend Running Successfully
            </div>
            <h1>AuraEstate Backend</h1>
            <p>Your Django API and Neon PostgreSQL database are live and operational.</p>
            <div class="links">
                <a href="/api/properties/" class="btn">
                    <span>Properties API</span>
                    <span class="tag">GET /api/properties/</span>
                </a>
                <a href="/api/properties/featured/" class="btn">
                    <span>Featured Properties</span>
                    <span class="tag">GET /api/properties/featured/</span>
                </a>
                <a href="/admin/" class="btn">
                    <span>Django Admin Panel</span>
                    <span class="tag">/admin/</span>
                </a>
            </div>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html_content)

urlpatterns = [
    path('', home_view, name='home'),
    path('admin/', admin.site.urls),
    path('api/', include('properties.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
