from django.db import models
from accounts.models import CustomUser
from django.core.validators import FileExtensionValidator


class OverallSentiment(models.Model):
    name_id = models.CharField(max_length=100,unique=True)
    pos_count = models.IntegerField()
    neg_count = models.IntegerField()
    neutral_count = models.IntegerField()
    overall_description = models.CharField(max_length=10000)

    input_file = models.FileField(upload_to='uploads/%Y/%m/%d',validators=[FileExtensionValidator(allowed_extensions=['txt'])])

    autor_id = models.ForeignKey(CustomUser,on_delete=models.CASCADE)

    is_public = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name_id