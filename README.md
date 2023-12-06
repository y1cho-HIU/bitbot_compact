<div align="center">
  
  # BITBOT
  본 프로젝트는 가상화폐 자동매매 프로젝트로 BITCOIN의 **BIT**와 ROBOT의 **BOT**을 합친 이름입니다.
  </br>본 프로그램은 바이낸스 [테스트넷](https://testnet.binancefuture.com/en/futures/BTCUSDT, "testnet")과 [실거래](https://www.binance.com/en/futures/BTCUSDT, 'real-mode')를 지원합니다.<br/>
  </br>
  
  
</div>

### 목차
1. [기본 정보](#기본-정보)
2. [시작 가이드](#시작-가이드)
3. [기술 스택](#기술-스택)
4. [실행 화면](#실행-화면)

### 기본 정보
**정보**
> 기본적으로 BITBOT은 네트워크가 연결된 상태에서 사용 가능합니다.
> 또한 가상화폐 거래소는 바이낸스를 사용하므로 시작 전 바이낸스 회원 가입과 선물 거래소 연결이 필요합니다.


**전략**
> 기본적으로 사용하는 전략은 envelope 지수를 활용한 변동성 돌파 매매 기법으로 필요한 파라미터는 다음과 같습니다.

|파라미터|설명|
|:---:|---|
|`sma_period`|이동평균선(SMA)의 기간을 결정하는 파라미터입니다.| 
|`env_weight`|ENVELOPE 전략의 가중치 값을 정하는 파라미터로 `position` 진입을 결정할 때 사용됩니다.|
|`rrr_rate`|ENVELOPE 전략의 위험보상비율(risk reward ratio)의 값을 결정하는 파라미터로 `loss_price`를 결정할 때 사용됩니다.|

**팀 소개**
|팀원명|담당|
|:---|:---|
|⭐[avatrue](https://github.com/avatrue, "avatrue_link")|전략 구성 및 머신러닝 파트 담당|
|👦[y1cho-HIU](https://github.com/y1cho-HIU, "y1cho_link")|개발 및 테스팅 파트 담당|

### 시작 가이드
**기본 설정**
1. 바이낸스(TESTNET 포함) 선물 로그인 및 API_KEY 발급
2. 위에서 언급한 기본 파라미터 수치 설정

**설치 방법 및 사용자 설정**
```
$ git clone https://github.com/y1cho-HIU/bitbot_compact.git
$ cd ./bitbot_compact
$ vim ./bitbot/json_repository/account.json    # account.json 설정
```
> account.json에 들어가 IP 정보와 API 정보, 그리고 파라미터를 입력합니다.
```json
{
  "ip_info": "0.0.0.0",
  "api_key": "YOUR_API_KEY",
  "api_secret": "YOUR_API_SECRET",
  "test_api_key": "YOUR_TEST_KEY",
  "test_api_secret": "YOUR_TEST_SECRET",
  "symbol": "YOUR SYMBOL",
  "sma_period": 10,
  "env_weight": 1,
  "rrr_rate": 1
}
```

**사용자 설정 및 실행**
```
$ python main.py 0    # testnet에서 테스팅을 진행합니다.
$ python main.py 1    # 실제 환경에서 실거래를 진행합니다.
```
> Flask로 거래 정보 확인하기 위해 새로운 cmd 창을 열어 다음과 같은 명령어를 입력합니다.
```
$ python ./bitbot_flask/app.py
```

### 기술 스택
<div align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=Python&logoColor=yellow">
  <img src="https://img.shields.io/badge/Anaconda-44A833?style=for-the-badge&logo=Anaconda&logoColor=white">
  <img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=Flask&logoColor=white">
  <img src="https://img.shields.io/badge/Jupyter-F37626?style=for-the-badge&logo=Jupyter&logoColor=white">
  <img src="https://img.shields.io/badge/Pytorch-EE4C2C?style=for-the-badge&logo=Pytorch&logoColor=white">
  <img src="https://img.shields.io/badge/AMAZON AWS-232F3E?style=for-the-badge&logo=amazonaws&logoColor=white">
</div>

### 실행 화면
**초기 화면**
<p align="center">
    <img src="https://github.com/y1cho-HIU/bitbot_compact/assets/101562660/b937b7b1-7823-45c6-b9a2-091340a8d775", width="600", height="800">
</p>

**Flask 화면**
<p align="center">
    <img src="https://github.com/y1cho-HIU/bitbot_compact/assets/101562660/c2a73368-6a60-4175-a167-0ddcf59c00fd", width="600", height="800">
</p>
