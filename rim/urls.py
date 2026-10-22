from django.urls import path
from .views import RIMProcessView, RIMHealthView
try:
    from .views import RIMOptimizerView
except ImportError:
    RIMOptimizerView = None

urlpatterns = [
    path('process/', RIMProcessView.as_view(), name='rim-process'),
    path('health/', RIMHealthView.as_view(), name='rim-health'),
]

if RIMOptimizerView:
    urlpatterns.append(path('optimize/', RIMOptimizerView.as_view(), name='rim-optimize'))

