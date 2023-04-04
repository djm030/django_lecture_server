gunicorn config.wsgi:application --daemon --access-logfile access.log --error-logfile error.log


gunicorn config.wsgi:application --daemon --bind 0.0.0.0:8000 --access-logfile access.log --error-logfile error.log


location /static/ {
        alias /var/www/crazyform.store/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }