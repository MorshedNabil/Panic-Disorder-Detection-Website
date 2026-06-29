from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .llm_advice import generate_panic_advice
from .ml_model.prediction import predict as predict_disorder
from django.conf import settings
import logging
import urllib.request
import urllib.parse
import os

logger = logging.getLogger(__name__)

# Create your views here.
def home(request):
    logger.info("Index page loaded")
    
    sentry_env = "production" if not settings.DEBUG else "development"
    
    return render(request, 'index.html', {
        'SENTRY_DSN': os.environ.get('SENTRY_DSN', ''),
        'SENTRY_ENV': sentry_env, # as in template the enviroment is not set so the JS can't handle the 'production' vs 'development' thing which is handled in  settings.py so we manually setting from view.py; that 'SENTRY_ENV' will be passed to the template as template variable
    })

@csrf_exempt
def sentry_tunnel(request):
    if request.method != 'POST':
        return HttpResponse(status=200)
    try:
        dsn = os.environ.get('SENTRY_DSN', '')
        if not dsn:
            return HttpResponse(status=400)

        parsed = urllib.parse.urlparse(dsn)
        project_id = parsed.path.strip('/')
        host = parsed.hostname  # e.g. o123.ingest.us.sentry.io

        url = f'https://{host}/api/{project_id}/envelope/'
        req = urllib.request.Request(
            url,
            data=request.body,
            headers={'Content-Type': 'application/x-sentry-envelope'},
            method='POST',
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            return HttpResponse(resp.read(), status=resp.status)
    except Exception:
        return HttpResponse(status=400)


def trigger_sentry_error(request):
    division_by_zero = 1 / 0
    return HttpResponse("This will never be reached due to the error above.")


@require_http_methods(["POST"])
def predict(request):
    try:
        # Create a dictionary from form data
        form_data = {
            'age': request.POST.get('age'),
            'lifestyle': request.POST.get('lifestyle'),
            'stressors': request.POST.get('stressors'),
            'symptoms': request.POST.get('symptoms'),
            'severity': request.POST.get('severity'),
            'impact': request.POST.get('impact'),
            'coping_mechanisms': request.POST.get('coping-mechanisms'),
            'family_history': request.POST.get('family-history'),
            'social_support': request.POST.get('social-support'),
            'personal_history': request.POST.get('personal-history'),
        }
        
        # Pass dictionary to predict function
        result = predict_disorder(form_data)
        advice = generate_panic_advice(form_data, result)

        # sentry log: for successful prediction
        logger.info("Model predicted properly")
        
        # Return JSON response with prediction results
        return JsonResponse({
            'success': True,
            'prediction': result.get('prediction'),
            'confidence': result.get('confidence'),
            'message': result.get('message'),
            'advice': advice.get('text'),
            'advice_source': advice.get('source'),
            'advice_error': advice.get('error'),
        }, status=200)
    
    except Exception as e:
        # sentry log: error for failed prediction
        logger.error("prediction failed", exc_info=True)

        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
