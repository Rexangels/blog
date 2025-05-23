# Generated by Django 5.1.7 on 2025-04-01 11:38

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_post_published_date_post_status_alter_post_content'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Bookmark',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('notes', models.TextField(blank=True, help_text='Personal notes about this bookmark')),
            ],
        ),
        migrations.CreateModel(
            name='CommentLike',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='PostLike',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bio', models.TextField(blank=True, max_length=500)),
                ('avatar', models.ImageField(blank=True, null=True, upload_to='profile_pics/')),
                ('website', models.URLField(blank=True)),
                ('twitter', models.CharField(blank=True, max_length=50)),
                ('github', models.CharField(blank=True, max_length=50)),
                ('linkedin', models.CharField(blank=True, max_length=50)),
                ('display_name', models.CharField(blank=True, max_length=50)),
                ('location', models.CharField(blank=True, max_length=100)),
                ('email_notifications', models.BooleanField(default=True)),
                ('notify_on_comment', models.BooleanField(default=True)),
                ('notify_on_reply', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ['-is_pinned', 'created_at']},
        ),
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ['-is_pinned', '-published_date', '-created_at']},
        ),
        migrations.AddField(
            model_name='comment',
            name='email',
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AddField(
            model_name='comment',
            name='ip_address',
            field=models.GenericIPAddressField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='comment',
            name='is_pinned',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='comment',
            name='like_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='comment',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='blog.comment'),
        ),
        migrations.AddField(
            model_name='comment',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('spam', 'Spam'), ('deleted', 'Deleted')], default='pending', max_length=10),
        ),
        migrations.AddField(
            model_name='comment',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='comment',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='comments', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='comment',
            name='user_agent',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='comment',
            name='website',
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name='post',
            name='bookmark_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='post',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='post',
            name='estimated_reading_time',
            field=models.PositiveIntegerField(default=0, editable=False, help_text='Estimated reading time in minutes'),
        ),
        migrations.AddField(
            model_name='post',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='post',
            name='is_featured',
            field=models.BooleanField(default=False, help_text='Feature this post on the homepage'),
        ),
        migrations.AddField(
            model_name='post',
            name='is_pinned',
            field=models.BooleanField(default=False, help_text='Pin this post to the top of lists'),
        ),
        migrations.AddField(
            model_name='post',
            name='like_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='post',
            name='show_table_of_contents',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='post',
            name='status',
            field=models.CharField(choices=[('draft', 'Draft'), ('published', 'Published'), ('archived', 'Archived')], default='draft', max_length=10),
        ),
        migrations.AddIndex(
            model_name='comment',
            index=models.Index(fields=['post', 'status'], name='blog_commen_post_id_651007_idx'),
        ),
        migrations.AddIndex(
            model_name='comment',
            index=models.Index(fields=['user'], name='blog_commen_user_id_dd6a39_idx'),
        ),
        migrations.AddIndex(
            model_name='comment',
            index=models.Index(fields=['parent'], name='blog_commen_parent__43ce68_idx'),
        ),
        migrations.AddIndex(
            model_name='post',
            index=models.Index(fields=['slug'], name='blog_post_slug_cdb902_idx'),
        ),
        migrations.AddIndex(
            model_name='post',
            index=models.Index(fields=['status', 'visibility'], name='blog_post_status_039d5f_idx'),
        ),
        migrations.AddIndex(
            model_name='post',
            index=models.Index(fields=['published_date'], name='blog_post_publish_205817_idx'),
        ),
        migrations.AddIndex(
            model_name='post',
            index=models.Index(fields=['-is_pinned', '-published_date'], name='blog_post_is_pinn_4de2c6_idx'),
        ),
        migrations.AddField(
            model_name='bookmark',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookmarks', to='blog.post'),
        ),
        migrations.AddField(
            model_name='bookmark',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookmarks', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='commentlike',
            name='comment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comment_likes', to='blog.comment'),
        ),
        migrations.AddField(
            model_name='commentlike',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comment_likes', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='postlike',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='likes', to='blog.post'),
        ),
        migrations.AddField(
            model_name='postlike',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='post_likes', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='blog_profile', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='bookmark',
            unique_together={('user', 'post')},
        ),
        migrations.AlterUniqueTogether(
            name='commentlike',
            unique_together={('user', 'comment')},
        ),
        migrations.AlterUniqueTogether(
            name='postlike',
            unique_together={('user', 'post')},
        ),
    ]
