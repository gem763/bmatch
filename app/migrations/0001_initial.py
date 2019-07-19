# Generated by Django 2.2.2 on 2019-07-19 13:30

import app.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomEmailUser',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(db_index=True, max_length=255, unique=True, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('fullname_kr', models.CharField(blank=True, max_length=120, null=True)),
                ('fullname_en', models.CharField(blank=True, max_length=120, null=True)),
                ('keywords', models.TextField(default='')),
                ('website', models.CharField(blank=True, max_length=200, null=True)),
                ('origin', models.CharField(blank=True, max_length=50, null=True)),
                ('awareness', models.FloatField(default=0)),
                ('category', models.CharField(blank=True, max_length=120, null=True)),
                ('description', models.TextField(blank=True, default='', null=True)),
                ('history', models.TextField(blank=True, default='', null=True)),
                ('logo', models.ImageField(default='', upload_to='brand_logos')),
            ],
        ),
        migrations.CreateModel(
            name='Hashtag',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('hashtag', models.CharField(max_length=120)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Option',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('optname', models.CharField(default='init', max_length=120)),
                ('idwords', models.TextField(default='[{"럭셔리": "럭셔리 고급 호화 과시 명품 luxury 비싼 고가 expensive pricy pricey", "캐주얼": "캐주얼 캐쥬얼 casual 스타일리시 스타일리쉬 stylish"}, {"유니크": "유니크 독특 독창 unique 개성 only 참신 신선 특이 아이디어 철학", "대중성": "대중 popular 널리 흔한 massive mass 대중성"}, {"정통성": "정통 클래식 classic 품격 약속 신뢰 믿음 예측 견고 품질 안정", "트렌디": "트렌디 트랜디 트렌드 트랜드 유행 trend trendy 변화 새로운 민감 예민 신상 최신"}, {"포멀": "포멀 formal 노멀 normal 평범 일상 무난 기본 베이스 베이직 base basic", "액티브": "화제 인기 hot 튀는 액티브 active 앞서가는 실험 과감 선도 선구 대담"}]')),
                ('api', models.CharField(default='http://127.0.0.1:8080/api', max_length=120)),
                ('id_scaletype', models.IntegerField(default='0')),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('image', models.ImageField(upload_to='posts/%Y/%m/%d/origin')),
                ('content', models.TextField(blank=True, max_length=500, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('brands_related', models.ManyToManyField(blank=True, to='app.Brand')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('profile_image', models.ImageField(default='', max_length=500, upload_to='')),
                ('worldcup', models.TextField(blank=True, default='{}', null=True)),
                ('initial_awared', models.TextField(blank=True, null=True)),
                ('brand_bookmarks', models.ManyToManyField(blank=True, related_name='brand_bookmarks_set', to='app.Brand')),
                ('brand_likes', models.ManyToManyField(blank=True, related_name='brand_likes_set', to='app.Brand')),
                ('level_tested', models.ManyToManyField(blank=True, related_name='leveltested_set', to='app.Brand')),
                ('myfavorite', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='myfavorite_set', to='app.Brand')),
                ('post_bookmarks', models.ManyToManyField(blank=True, related_name='post_bookmarks_set', to='app.Post')),
                ('post_likes', models.ManyToManyField(blank=True, related_name='post_likes_set', to='app.Post')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Feed',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('nlikes', models.IntegerField(default='0')),
                ('content', models.TextField(blank=True, max_length=1000, null=True)),
                ('feed_image', models.ImageField(upload_to=app.models.feed_image_path)),
                ('author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.Profile')),
                ('hashtags', models.ManyToManyField(blank=True, to='app.Hashtag')),
                ('membership', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.Brand')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CommentPost',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('content', models.TextField(blank=True, max_length=500, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('post', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='app.Post')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CommentBrand',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('content', models.TextField(blank=True, max_length=500, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('brand', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='app.Brand')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
