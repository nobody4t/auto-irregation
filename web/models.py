from django.db import models
    
class GrassEnvironment(models.Model):
    Time = models.DateTimeField()
    Temp = models.DecimalField(max_digits=5, decimal_places=1)
    Hum = models.DecimalField(max_digits=5, decimal_places=1)

    def __str__(self):
        return f"Time: {self.Time}, Temp: {self.Temp}, Hum: {self.Hum}"
    
class AnimalRecord(models.Model):
    Time = models.DateTimeField()
    Record = models.CharField(max_length = 254)

    def __str__(self):
        return f"Time: {self.Time}, Record: {self.Record}"