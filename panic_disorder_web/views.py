from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .ml_model.prediction import predict

# Create your views here.
def home(request):
    return render(request, 'index.html')

@require_http_methods(["POST"])
def assess(request):
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
        result = predict(form_data)
        
        # Return JSON response
        return JsonResponse({
            'success': True,
            'prediction': result,
            'message': 'Assessment completed successfully'
        }, status=200)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
