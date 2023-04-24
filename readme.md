gunicorn config.wsgi:application --daemon --access-logfile access.log --error-logfile error.log


gunicorn config.wsgi:application --daemon --bind 0.0.0.0:8000 --access-logfile access.log --error-logfile error.log


location /static/ {
        alias /var/www/crazyform.store/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }


📌0. 일정 및 목표
📅프로젝트 일정

사전 기획 : 2월 24일 ~ 2월 28일
기간 : 3월1일 ~ 4월 3일
📌1. 프로젝트 소개
목표 : 강의 사이트를 개발후 배포까지 완료
사용 기술 :
FRONT-END : react , react-query , react-hook-form , chakra-UI , react-player , scss
BACK-END : django , nginx, certbot, NCP(네이버 클라우드 플랫폼)서버, Rest-framework, mysql, ObjectStorage(NCP 에서 아마존의 S3), simple-jwt
📌2. 팀 소개 및 역할
요번 프로젝트는 팀원은 6명이였다. 대신 저번 프로젝트와는 다르게 프론트와 백엔드의 역할을 완전히 나누어 3명은 백엔드, 3명은 프론트엔드로 나누어서 개발을 진행하였다. 나는 여기서 백엔드를 맡아서 진행하였고 팀장이 되어서 전체적인 관리까지 같이 진행하였다.

🎪BACK-END
전체 프로젝트의 진행 상황을 추적하고, 일정과 예산을 관리
팀원들 사이의 커뮤니케이션을 원활하게 유지하는 역할
장고를 사용하여 웹 애플리케이션의 서버 측 로직을 개발.
데이터베이스 모델, API, 인증 및 권한 관리, 로직 등을 구현
서버, 데이터베이스 및 다른 인프라 구성요소를 관리
필수 기능
전체 강의 보기
디테일 페이지 구현
댓글 / 대댓글 달기
장바구니
결제
서버 배포
영상 스트리밍
회원가입
회원정보 수정
내가 구매한 강의 보기
검색 기능
비디오 올리기
강의 올리기
jwt 로그인 유지
로그 데이터 남기기
📌3. 협업방법
사용 프로그램 : 깃허브, 디스코드, 노션
깃허브 : 코드 공유
백엔드 : https://github.com/djm030/LectureProject-django
API 문서 : https://www.crazyform.store/swagger/
프론트 : https://github.com/blairMoon/front-lecture-project
디스코드 : 소통 및 요청사항 정리


노션 : 회의록 및 기능 개발 정리
📌4. 개발 과정
1. 기능및 요구사항 정리
📍회의 및 토의




첫번쨰로 우리가 강의 사이트를 만들떄 어떠한 기능을 넣을지 어떠한 구성을 할지 회의를 진행하였다.

📍유저 다이어그램

어떻게 만들어야 할지 유저가 어떠한 경험을 할지를 중점으로 유저 다이어 그램을 만들었다.

2. DB설계

유저 다이어 그램과 요구사항을 정리해서 데이터 모델링 과정을 거쳐 DB를 설계했다.

📍 서버 플로우




📍 간트차트


📌5. 결과물
배포 페이지 주소 : https://www.crazyform.shop/
백엔드 페이지 주소 : https://www.crazyform.store/

📌6. 문제해결 및 코드작성
💡모델 및 api 구성 // 프론트 엔드 와의 소통
처음 우리가 데이터 모델링을 하고 난뒤에 db가 지속적으로 바뀌었다. 그러다 보니 우리가 아무리 개발을 진행하여도 프론트에서는 변경된 모델이나 데이터를 바로바로 사용하기가 어려웠고 배포를 마지막에 하다 보니깐 협업이 생각보다 어려웠다.
이러한 상황을 해결하기 위해서 liveshare를 사용했다.
원격으로 협업하고 실시간으로 코드를 공유할 수 있게 해주는 도구이고, 이 기능을 사용하면, 팀원들이 서로의 코드를 볼 수 있으며, 함께 디버깅하여 문제를 해결할수 있었다.

💡오브젝트 storage 연결
NCP 에서의 S3 인 Object Storage를 사용하니깐 일단 자료가 매우 부족하였다. 그래서 어떻게 해야하나 고민하다가 코드를 찾아 우리 프로젝트에 연결하였다.

# S3 storage settings
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = "lecture-site-video"
AWS_S3_REGION_NAME = "ap-northeast-2"
AWS_S3_ENDPOINT_URL = "https://kr.object.ncloudstorage.com"
찾아 보니 장고는 이미 aws s3 연결을 지원하는 설정이 있었고, NCP도 이에 따라서 S3설정에 맞춰서 신청하면 거의 비슷하게 사용할수 있도록 만들었다.

# 비디오를 올리면 그 파일을 ObjectStorage에 올리고 그url을 db에 저장하는 클래스
class UploadVideoView(APIView):
    def post(self, request, lectureId):
        file = request.FILES.get("file")
        if file:
            lecture = Lecture.objects.get(LectureId=lectureId)
            cal_lec = CalculatedLecture.objects.get(lecture=lecture)
            # Upload the file to ObjectStorage
            s3 = boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_ACCESS_KEY_ID,
            )
            file_name = default_storage.save(file.name, file)
            file_path = os.path.join(default_storage.location, file_name)
            bucket_name = settings.AWS_STORAGE_BUCKET_NAME
            s3.upload_file(file_path, bucket_name, file_name)

            # Get the video URL from ObjectStorage
            video_url = f"https://{bucket_name}.s3.amazonaws.com/{file_name}"

            # Calculate the video length
            video_clip = VideoFileClip(file_path)
            video_length = video_clip.duration
            video_clip.close()

            # Save the video information in the database
            video = Video(
                title="Title",
                description="Description",
                videoFile=video_url,
                videoLength=video_length,
                calculatedLecture=cal_lec,
            )
            video.save()

            # Return the serialized video object
            serializer = serializers.VideoSerializer(video)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            {"error": "File not provided"}, status=status.HTTP_400_BAD_REQUEST
        )
💡DB 연결
원래는 db 서버를 만들어서 따로 배포한후 연결하려고 했지만 오히려 그게 더 어렵다는 사람들의 의견을 듣고 수정하였다. 또 원래는 postgre를 사용해 django와 연결하려고 했지만, 우분투 리눅스 상에서 에러가 지속적으로 발생해 , mysql로 변경하였다.

DATABASES = {
   "default": {
       "ENGINE": "django.db.backends.sqlite3",
       "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
   }
}

if not DEBUG:
   DATABASES = {
       "default": {
           "ENGINE": "django.db.backends.mysql",
           "NAME": "lecturesite_db",
           "USER": "root",
           "PASSWORD": os.environ.get("DB_PASSWORD"),
           "HOST": "localhost",
           "PORT": "3306",
           "OPTIONS": {
               "charset": "utf8mb4",
           },
       }
   }
그래서 로컬환경에서는 디버그를 하므로 이떄는 sqlite를 사용하여 간단한 작업을 하고 아닐떄는 mysql을 사용할수 있도록 설정을 만들었다.

💡백엔드 서버 배포
💡nginx
이번에 새로 nginx를 사용해 봤는데 생각보다 패치가 잘 안되서 어려움이 많았다. 또 아직 도커에 대한 공부가 안되어서 사용하지 못해서 설정을 잡는데 어려움이 많았다.

server {
    server_name crazyform.store www.crazyform.store;

    # root 디렉토리와 index 파일 설정
    root /root/server;
    index index.html index.htm;

    # access 및 error 로그 위치 설정
    access_log /var/log/nginx/crazyform.store.access.log;
    error_log /var/log/nginx/crazyform.store.error.log;

    # 정적 파일에 대한 MIME 타입 설정
    include /etc/nginx/mime.types;

    # 오류 페이지 설정
    error_page 404 /404.html;
    error_page 500 502 503 504 /50x.html;
    location = /50x.html {
        internal;
    }
    # location /api/ {

    # proxy_pass http://127.0.0.1:8000/;
    # }
    location /static/ {
        alias /var/www/crazyform.store/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }

    # 서버에서 제공되는 모든 파일에 대한 location 블록 설정
    location / {
        try_files $uri $uri/ @proxy;
    }

    location @proxy {
        proxy_pass 내IP:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    listen 443 ssl; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/crazyform.store/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/crazyform.store/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
}
💡gunicorn
원래라면 python manage.py runserver 익숙한 명령어로 장고를 실행했겠지만 여기에는 두가지 큰 단점이 존재했다. 첫쨰로 ssh 접속이 끊기면 장고 배포도 꺼지는 문제가 생겼고 두번째로 백그라운드에서 진행 하지 않으면 켜둔상태로는 아무 작업도 할수 없는 점이였다. 따라서 이러한 문제를 해결하기 위해 gunicorn을 사용해 서버 배포를 진행하였다.

gunicorn config.wsgi:application --daemon --access-logfile access.log --error-logfile error.log

gunicorn config.wsgi:application --daemon --bind 0.0.0.0:8000 --access-logfile access.log --error-logfile error.log
💡certbot 인증 https
처음 서버를 제대로 배포해 보면서 nginx와 gunicorn으로 배포만 하면 모든 문제가 해결될줄 알았다. 하지만 리액트나 장고에서 서로 rest api 통신을 위해서는 https 보안 통신을 진행했어야 했다. 따라서 내가만든 서버에 무료로 인증서를 발급해주는 certbot을 도입해 이문제를 해결하였다.

sudo certbot certonly --standalone -d example.com -d www.example.com
이떄의 도메인은 카페24에서 구매해 적용하였다.

💡프론트엔드 서버 패포
server {
    listen 443 ssl;
    server_name crazyform.shop www.crazyform.shop;
    root /var/www/html/build/;

    location / {
    try_files $uri $uri/ /index.html?$args;
    } 

    error_page 404 /404.html;
    error_page 500 502 503 504 /50x.html;

    location = /50x.html {
        root /usr/share/nginx/html;
    }

    access_log /var/log/nginx/crazyform.shop-access.log;
    error_log /var/log/nginx/crazyform.shop-error.log;

    ssl_certificate /etc/letsencrypt/live/www.crazyform.shop/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/www.crazyform.shop/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
}

server {
    listen 80;
    server_name crazyform.shop www.crazyform.shop;
    return 301 https://$host$request_uri;
}
원래는 프론트 백 서버를 나누지않고 한꺼번에 진행하려고 하였다가 각각의 서버를 배포하는것도 재밌을거 같아서 두개로 나누어서 배포하였다. 그런데 이번에는 리액트의 빌드 파일을 읽지 못하는 문제가 나타났다. 원인은 내가 root 사용자 이외에 다른 사용자를 만들지 않고 진행하여서 conf 파일이 읽을 권한이 없어서 빌드파일을 읽지 못하였다. 이문제를 해곃하기 위해서
/var/www/html/build/; 이 위치로 빌드파일을 따로 이동시켜서 문제를 해결하였다.

💡JWT 토큰
이번에 로그인 유지를 위해 JWT 토큰을 사용하기로 하였다. 장고에서는 이미 simple jwt라는 서드파티 앱이 존재해서 이를 사용하였다.

    path(
        "jwt-token-auth/", TokenObtainPairView.as_view(), name="token_obtain_pair"
    ),  # 로그인
    path(
        "jwt-token-auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"
    ),  # 리프레시=> 액세스
    path(
        "jwt-token-auth/verify/", TokenVerifyView.as_view(), name="token_verify"
    ),  # 유저인증
📌7. KPT회고
🗨️ Keep
👏 API 설계
이번에 정말 제대로 강의사이트 하나 정도의 큰 프로젝트에서 쓸만한 api전체를 만져본거 같다. 생각보다 원하는 데이터도 많고 처음 생각했던것 이외에도 다른 데이터를 보내줄것도 많았는데 프론트에서 원하는 데이터 전체를 잘 보내준거 같다.
이번에 API 설계를 거의다 해보면서 MVC (모델-뷰-컨트롤러) 패턴에 대해서 좀더 깊게 이해할수 있게 되었다.
이번에 프론트엔드하고 많은 소통을 해보면서 오히려 내가 프론트엔드에 대한 이해가 많이 늘어난 느낌이였다. 이러한 데이터가 필요하고 또 이러한 데이터는 어떤 방식으로 보내주면 좋은지 많이 느꼈다.
👏 서버배포
서버 배포도 내손으로 직접 해보면서 어려워서 방치해 두었던 nginx 나 gunicorn 또 certbot 과 도메인 등록까지 배포에 필요한 모든것을 간단하게나마 경험해 본것 같다.
또 직접 NCP에 들어가서 서버를 구매하고 등록하고 port 설정해주고 규칙까지 설정해 주면서 이런 서버 사용경험이 많이 들어간거 같아서 좋았다.
👏 영상 처리
어떻게 영상을 스트리밍 해서 보여줄지 처음 강의사이트를 제작한다고 결정했을때부터 정말 고민이 많아서 그냥 유튜브링크로 보내줘야 할지 고민이 많았는데 Object Storage를 이용해 스트리밍처리를 해서 영상처리를 직접 관리할수 있어서 정말 잘했다고 생각한다.
👏 원활한 소통
이번에 정말 힘들었지만 그래도 팀원들과 소통이 제일 잘 된 팀인거 같아서 좋았다. 6명 모두 각자가 할수있는 한 최선을 다해서 해준 느낌이라서 팀장으로서 다행이라고 생각한다.
🗨️ Problem
✋ 깔끔하지 않은 코드
이번에 한달이라는 시간동안 만들어 보면서 생각보다 시간이 너무 없었다. 그러다 보니 코드가 깔끔하지 않고 데이터를 보내줄떄도 필요한 데이터 이외에도 필요없는 데이터가 보내진다던지 하는점이 아쉬웠다.
✋ 보안상의 문제
빠르게 완성만 진행하다 보니 보안상 문제가 생길만한 점이 많이 보였다. 예를 들어 jwt 토큰을 우리가 이번에 사용하였지만, 액세스나 리프레시 토큰이 쿠키에 그대로 저장한다던지 아니면 쉽게 탈취가 가능하다던지 문제가 있어서 이를 보완해야 할거같다.
✋ 테스트 코드의 부재 / 트래픽 경험 부재
이번에 직접 크롤링을 통해서 데이터를 집어 넣었지만 테스트 코드를 작성해보지 못해서 아쉬웠다. 또 배포는 진행했지만 이걸 여러사람들에게는 배포해보지 못해서 트래픽이 많아지면 어떻게 되는지 실험해보지 못했다. 다른 툴을 써보면 가능하겠지만 시간상 이것또한 진행하지 못했다.
✋ 시간상 완성하지 못한 부분
장바구니 라던지 결제라던지 원래 우리가 구현을 완성 시키려던 몇가지 부분을 진행하지 못한 부분이 많아서 아쉬웠다.
🗨️ Try
🔥 도커 + 젠킨스
이번에 서버에서 시간을 정말 많이 버리면서 도커의 중요성을 정말 뼈저리게 느꼈다. 프로젝트를 보완한다면 도커를 이용하여서 배포 시간을 줄이고 젠킨스를 통해 자동배포 (CI/CD) 를 진행해 볼 예정이다.
🔥 데이터 시각화
어느정도 배포도 완료 되었고 뼈대는 있기 때문에 만약 보완한다면 데이터 시각화를 통해 사용 경험을 늘리는것이 어떨지 시도해볼 예정이다.
🔥 데이터 파이프라인 개선
원본 데이터를 가져와서 목적지에 사용 가능한 형태로 변환하는 과정을 자동화하여, 데이터 엔지니어, 데이터 사이언티스트, 비즈니스 분석가들이 더 효율적으로 작업할수 있도록 할것이다.
NCP에서 제공하는 'Data Lake' , 'Machine Learning', 'Cloud Functions' 를 사용해볼 예정이다.
🔥 이외에 완성되지 못한 부분 개선
장바구니, 결제, 관리자/강사 페이지 제작
📌8. 프로젝트 발표
발표영상 링크
