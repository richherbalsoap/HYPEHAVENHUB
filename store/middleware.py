import time
import logging
from django.core.cache import cache
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.utils.deprecation import MiddlewareMixin
from .exceptions import AtelierException

logger = logging.getLogger(__name__)

class RateLimitMiddleware(MiddlewareMixin):
    """
    Rate limits POST request rates per client IP for authentication and checkout paths.
    Fails open if cache backend goes offline.
    """
    def process_request(self, request):
        if request.method == 'POST' and any(path in request.path for path in ['/login/', '/verify-otp/', '/place-order/']):
            # Exclude django admin panel from rate limiting
            if request.path.startswith('/admin/'):
                return None
                
            # Extract client IP address
            ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', '')).split(',')[0].strip()
            key = f"rate_limit_{ip}_{request.path}"
            
            try:
                # Set rate limit window (max 5 requests per 60 seconds)
                request_times = cache.get(key, [])
                now = time.time()
                request_times = [t for t in request_times if now - t < 60]
                
                if len(request_times) >= 5:
                    logger.warning(f"Rate limit exceeded for IP {ip} on {request.path}")
                    if request.headers.get('Content-Type') == 'application/json' or request.headers.get('HX-Request') or request.path.startswith('/api/'):
                        return JsonResponse({"error": "Too many requests. Please wait a minute before retrying.", "code": "rate_limit_exceeded"}, status=429)
                    return HttpResponse("Too many requests. Please try again in a minute.", status=429)
                    
                request_times.append(now)
                cache.set(key, request_times, 60)
            except Exception as e:
                # Fail open to prevent application crash if Redis or cache is offline
                logger.error(f"Rate limiting cache check failed: {str(e)}")
        return None


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Applies custom Content-Security-Policy (CSP) and referrer headers to responses.
    """
    def process_response(self, request, response):
        csp_parts = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://checkout.razorpay.com https://*.razorpay.com https://checkout-ui.shiprocket.com https://*.shiprocket.com https://*.shiprocket.in https://shiprocket.in https://*.fastrr.com https://fastrr.com https://*.otpless.com https://otpless.com https://www.googletagmanager.com https://www.google-analytics.com",
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net https://cdnjs.cloudflare.com",
            "font-src 'self' data: https://fonts.gstatic.com https://cdnjs.cloudflare.com",
            "img-src 'self' data: https://*.r2.dev https://*.googleusercontent.com https://*.supabase.co https://*.neon.tech https://*.cloudinary.com https://*.s3.amazonaws.com https://*.r2.cloudflarestorage.com https://*.razorpay.com https://*.shiprocket.com https://*.shiprocket.in https://shiprocket.in https://*.fastrr.com https://fastrr.com https://www.google-analytics.com",
            "connect-src 'self' https://api.postalpincode.in https://api.zippopotam.us https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://*.r2.cloudflarestorage.com https://checkout-api.shiprocket.com https://*.shiprocket.com https://*.shiprocket.in https://shiprocket.in https://*.fastrr.com https://fastrr.com https://*.cred.club https://cred.club https://*.google.com https://*.otpless.com https://otpless.com https://api.razorpay.com https://*.razorpay.com https://www.google-analytics.com",
            "media-src 'self' https://*.r2.dev https://*.r2.cloudflarestorage.com",
            "frame-src 'self' https://api.razorpay.com https://*.razorpay.com https://*.otpless.com https://otpless.com https://*.shiprocket.in https://shiprocket.in",
            "object-src 'none'",
            "base-uri 'self'",
            "form-action 'self'",
        ]
        response['Content-Security-Policy'] = "; ".join(csp_parts)
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        return response


class ExceptionHandlingMiddleware(MiddlewareMixin):
    """
    Intercepts custom exceptions and formats responses cleanly for users or APIs.
    """
    def process_exception(self, request, exception):
        if isinstance(exception, AtelierException):
            logger.warning(f"Application error: {exception.message} (Code: {exception.code})")
            
            # Check if JSON or AJAX request
            if request.headers.get('Content-Type') == 'application/json' or request.headers.get('HX-Request') or request.path.startswith('/api/'):
                return JsonResponse({
                    "error": exception.message,
                    "code": exception.code
                }, status=exception.status_code)
                
            # Render a fallback error HTML page
            return render(request, 'errors/error_detail.html', {
                'message': exception.message,
                'code': exception.code
            }, status=exception.status_code)
            
        # Let default Django exception handler process other exceptions
        return None
