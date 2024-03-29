# Generated by Django 3.2.22 on 2023-11-14 15:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feedbacks', '0001_initial'),
        ('medias', '0002_file_caption'),
        ('works', '0009_alter_taskstep_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='taskstep',
            name='comments',
            field=models.ManyToManyField(related_name='task_step_comments', to='feedbacks.Comment'),
        ),
        migrations.AddField(
            model_name='taskstep',
            name='images',
            field=models.ManyToManyField(related_name='task_step_images', to='medias.File'),
        ),
        migrations.AddField(
            model_name='taskstep',
            name='videos',
            field=models.ManyToManyField(related_name='task_step_videos', to='medias.File'),
        ),
    ]
