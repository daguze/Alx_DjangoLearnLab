# SECURITY: Enforce HTTPS cookies to prevent interception
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# SECURITY: Protect against XSS and clickjacking
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True

# SECURITY: Content Security Policy
CSP_DEFAULT_SRC = ("'self'",)  # Only allow resources from our domain
