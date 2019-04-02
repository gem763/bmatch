# Generated by Django 2.1.5 on 2019-04-02 17:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_remove_brand_cluster'),
    ]

    operations = [
        migrations.CreateModel(
            name='Options',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('idwords', models.TextField(default="{\n        {'럭셔리': '럭셔리 고급 호화 과시 명품 luxury 비싼 고가 expensive pricy pricey',\n         '캐주얼': '캐주얼 캐쥬얼 casual 스타일리시 스타일리쉬 stylish'},\n        {'유니크': '유니크 독특 독창 unique 개성 only 참신 신선 특이 아이디어 철학',\n         '대중성': '대중 popular 널리 흔한 massive mass 대중성'},\n        {'정통성': '정통 클래식 classic 품격 약속 신뢰 믿음 예측 견고 품질 안정',\n         '트렌디': '트렌디 트랜디 트렌드 트랜드 유행 trend trendy 변화 새로운 민감 예민 신상 최신'},\n        {'포멀': '포멀 formal 노멀 normal 평범 일상 무난 기본 베이스 베이직 base basic',\n         '액티브': '화제 인기 hot 튀는 액티브 active 앞서가는 실험 과감 선도 선구 대담'}\n    }")),
            ],
        ),
    ]
