## Proje Hakkında
Projede database e ve önbelleğe yazdırılan veriler kullanılarak 3 farklı web servisi oluşturulmaktadır. Bu servislerden birinde önce önbellek kontrol edilir ve eğer veri varsa oradan veriyi çekerek belirli bir formatta web servisine gönderir eğer veri yoksa da direkt database üzerinden çektiği veriyi belirli bir formatta web servisine gönderir. 2. ve 3. web servisi uygulamasında ise database deki 2 farklı argüman ayrı ayrı translate edilerek web servisine sunulur. 

## Kullanılan Kütüphaneler ve İndirme Linkleri
[![Used Library](https://img.shields.io/badge/library-psycopg2-blue)](https://pypi.org/project/psycopg2/)
[![Used Library](https://img.shields.io/badge/library-elasticsearch_dsl-blue)](https://pypi.org/project/elasticsearch-dsl/)
[![Used Library](https://img.shields.io/badge/library-Flask-blue)](https://pypi.org/project/Flask/)
[![Used Library](https://img.shields.io/badge/library-SQLAlchemy-blue)](https://pypi.org/project/SQLAlchemy/)
[![Used Library](https://img.shields.io/badge/library-flask_sqlalchemy-blue)](https://pypi.org/project/Flask-SQLAlchemy/)
[![Used Library](https://img.shields.io/badge/library-jsonify-blue)](https://pypi.org/project/jsonify/)

## Versiyonlar
- Flask==3.0.0
- Flask-SQLAlchemy==3.1.1
- redis==5.0.1
- python==3.10.11

## Kullanım
Projeyi çalıştırınca postman üzerinden eğer breakdown/list servisine istek atarsanız bütün datayı json formatında görürsünüz. Eğer section/translate ya da state/translate servisine istek atarsanız belirli argümanların türkçe karakterlerle yazılmış halini görmüş olursunuz.

## Environment Variables

### Redis Variables
- host name: "REDISHOST"
    - value= "localhost"
- port: "REDIS_PORT"
    - value= "6379"
- db: "REDIS_DB_VALUE"
    - value= "0"
- password: "REDIS_PSWRD"
    - value= "redis_password"

### Database Variables
* SQLALCHEMY_DATABASE_URI: "DATABASE_URL"
    * value= "postgresql://cargo:cargodb.12345@cargo-db.staj.svc.cluster.mantam/cargo"

