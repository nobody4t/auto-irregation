from django.urls import path
from . import views

urlpatterns = [
    path('getnowdata/', views.GetSensordataandAutoControl().GetNowData, name="getnowdata"),
    path('getmysqldata/', views.GetSensorData, name="getmysqldata"),
    path('changeinterval/', views.GetSensordataandAutoControl().ChangeInterval, name="changeinterval"),
    path('changethreshold/', views.GetSensordataandAutoControl().ChangeThreshold, name="changethreshold"),
    path('valvecontrol/', views.GetSensordataandAutoControl().ValveControl, name="valvecontrol"),

    path('sendvideostream/', views.ProcessImage().SendVideoStream, name="sendvideostream"),
    path('get30animalrecords/', views.Get30AnimalRecords, name="get30animalrecords"),

    path('generaltxt/', views.GeneralTXT, name="generaltxt"),
    path('dltxt/<str:filename>/', views.download_txt),

]