from django.db import models


class SingletonModel(models.Model):
    """
    Модель, которая всегда имеет только один экземпляр.
    """

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.__class__.objects.exists() and not self.id:
            existing = self.__class__.objects.first()
            for field in self._meta.fields:
                if field.name != 'id':
                    setattr(existing, field.name, getattr(self, field.name))
            existing.save()
        else:
            super(SingletonModel, self).save(*args, **kwargs)

    @classmethod
    def load(cls):
        if not cls.objects.exists():
            cls.objects.create()
        return cls.objects.get()


class SingleModel(SingletonModel):
    title = models.CharField(max_length=123, verbose_name='Название')
    procent = models.FloatField(verbose_name='Процент')
    mail = models.EmailField(verbose_name='Почта')
    canal = models.CharField(max_length=123, verbose_name="Канал тг")
    podderjka = models.CharField(max_length=123, verbose_name="Ссылка на поддержку")


    def __str__(self):
        return 'Контактная информация'

    class Meta:
        verbose_name = 'Общие данные'
        verbose_name_plural = 'Общие данные'


NAME_CHOICES = [
    ('kg', 'kg'),
    ('kz', 'kz'),
    ('uz', 'uz'),
]

class Recvisity(models.Model):
    region = models.CharField(verbose_name='Регион', choices=NAME_CHOICES, max_length=2)
    title = models.CharField(verbose_name='Название', max_length=123)
    number = models.CharField(max_length=123, verbose_name='Карта или номер')
    account = models.CharField(max_length=123, verbose_name='Чья карта, чтобы мы знали')

    def __str__(self):
        return f'{self.title} - {self.region} - {self.number}'

    class Meta:
        verbose_name = 'Реквизит'
        verbose_name_plural = 'Реквизиты'


class Order(models.Model):
    price = models.FloatField()
    region = models.CharField(choices=NAME_CHOICES, max_length=2)
    user_id = models.CharField(max_length=123)
    username = models.CharField(max_length=123)
    good_id = models.CharField(max_length=123)
    order_id = models.CharField(max_length=123)
    link = models.TextField()
    status = models.CharField(max_length=123)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, )

    def __str__(self):
        return f'{self.pk} - {self.user_id}'

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']

