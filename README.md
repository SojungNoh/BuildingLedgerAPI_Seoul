# BuildingLedgerAPI_Seoul
서울시 건축물대장 API 수집을 위한 코드.

건축물대장 API는 10개 종류의 파일로 분리 되어있다. 이 파일들은 행정구역을 기본 단위로 수집할 수 있다.
`BuildingLedgerAPI_Seoul`은 1000개 아이템을 기본 단위로 API 페이지들을 호출하고, 각각의 건축물대장 종류별 DataFrame을 최종 결과로 내놓는다.
한 종류당 작업시간이 20분 이상 소요되기도 하는데, 작업을 동시에 처리하기 위해 `multiprocessing`을 사용해 시간을 단축하고자 했다.

## Input
- ServiceKey : API를 호출하기 위한 고유 Key 값. 참고로 공공데이터포털에서 개발계정은 하루 트래픽 횟수가 제한되어있으니, 운영계정으로 전환할 것(일일 트래픽 1,000,000)을 추천한다.
- Operation : 10개의 건축물대장 중 어떤 것을 사용할 것인지. (건축물대장 표제부, 기본개요, 총괄표제부, 층별개요, 부속지번, 전유공용면적, 오수정화시설, 주택가격, 전유부, 지역지구구역)
- Land_code : 서울시 25개 집계구

## Output
- 구별 Operation에 따른 DataFrame CSV 파일


## Warning
가끔 에러가 나는 경우가 있는데, 그럴 경우 `multiprocessing`을 사용하지 말고 일반적인 방법으로 `dataframe_gu` 모듈을 사용하길 권장한다.
