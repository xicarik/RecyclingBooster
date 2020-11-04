from django.db import models

from django.contrib.auth.models import User

from djgeojson.fields import PointField

# Create your models here.

class Contribution(models.Model):
    waste_type = models.CharField(max_length=30)
    adress = models.CharField(max_length=50)
    photo_url = models.CharField(max_length=500)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, blank=True, null=True)

class RecycleSpot(models.Model):
    geom = PointField()
    point_type = models.IntegerField()
    waste_type = models.IntegerField()
    adress = models.CharField(max_length=200)
    link = models.CharField(max_length=500)
    
    @property
    def popup_content(self):
        return '<h3>{}</h3><h4>{}</h4><p>{}</p><a href="{}">Офиц. сайт</a>'.format(
            'Контейнер' if self.point_type == 0 else 'Пункт переработки',
            {0: 'Не пластик', 1: '1-PET Полиэтилен', 2: '2-PE-HD Полиэтилен высокой плотности',
             3: '3-PVC Поливинилхлорид', 4: '4-PE-LD Полиэтилен низкой плотности',
             5: '5-PP Полипропилен', 6: '6-PS Полистирол', 7: '7 Другие пластики'}[self.waste_type],
            self.adress,
            self.link
        )

class Article(models.Model):
    title = models.CharField(max_length=100)
    text = models.TextField(max_length=10000)
    recomendations = models.TextField(max_length=10000)
    photo_url = models.CharField(max_length=500)
    source_url = models.CharField(max_length=500)
    waste_type = models.IntegerField()
    
class Comment(models.Model):
    waste_type = models.IntegerField()
    text = models.TextField(max_length=5000)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, blank=True, null=True)
    creation_date = models.DateTimeField()
