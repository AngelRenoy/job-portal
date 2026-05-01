"""
WSGI config for smarthire project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smarthire.settings')

application = get_wsgi_application()

try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
    if not User.objects.filter(username='admin').exists():
        admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        admin_user.role = 'admin'
        admin_user.save()
        print("Superuser 'admin' created automatically.")
    else:
        admin_user = User.objects.get(username='admin')
        if admin_user.role != 'admin':
            admin_user.role = 'admin'
            admin_user.save()
            print("Updated existing admin role to 'admin'.")
except Exception as e:
    print(f"Skipping superuser creation: {e}")
