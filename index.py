import os
import sys
import ssl
import platform
import chromedriver_autoinstaller

ssl._create_default_https_context = ssl._create_unverified_context

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from dotenv import load_dotenv

# 설정된 driver를 반환하는 함수
def get_driver():
    # 현재 크롬 버전
    current_version = chromedriver_autoinstaller.get_chrome_version().split('.')[0]
    # 크롬 드라이버 설치 경로
    chrome_driver = f'./{current_version}/chromedriver'

    # 최신 버전이 설치 안 된 경우
    if not os.path.exists(chrome_driver) and not os.path.exists(chrome_driver + '.exec'):
        ssl._create_default_https_context = ssl._create_unverified_context
        print(f'Chrom driver is installed, version is {current_version}: {chrome_driver}')
        chromedriver_autoinstaller.install(True)

    # 드라이버 옵션 설정
    options = webdriver.ChromeOptions()
    options.add_argument('headless') # 브라우저 띄우기 x
        
    # 드라이버 설정
    driver = webdriver.Chrome(service=Service(chrome_driver), options=options)

    # 드라이버 반환
    return driver

# 소셜 로그인 함수
def social_login(id, pwd, github):
    if not github:
        return False

    # 소셜 로그인 페이지로 이동
    social_login_page = 'https://github.com/login'
    driver.get(social_login_page)

    # xpath 초기화
    input_id_xpath = '//*[@id="login_field"]'
    input_pwd_xpath = '//*[@id="password"]'
    login_button_xpath = '//*[@id="login"]/div[4]/form/div/input[12]'

    # 아이디 입력
    input_id = driver.find_element(by=By.XPATH, value=input_id_xpath)
    input_id.send_keys(id)

    # 비밀번호 입력
    input_pwd = driver.find_element(by=By.XPATH, value=input_pwd_xpath)
    input_pwd.send_keys(pwd)

    # 소셜 로그인
    login_button = driver.find_element(by=By.XPATH, value=login_button_xpath)
    login_button.send_keys(Keys.RETURN)

    # 프로그래머스 로그인 페이지로 이동
    programmers_login_page = 'https://programmers.co.kr/account/sign_in'
    driver.get(programmers_login_page)

    try:
        # 소셜 로그인 버튼 클릭
        login_button_xpath = f'//*[@id="main-app-account"]/div/div[2]/div/div[2]/div[1]/div/div[2]/div[5]/div[2]/form[2]/button'
        login_button = driver.find_element(by=By.XPATH, value=login_button_xpath)
        login_button.send_keys(Keys.ENTER)
    except:
        # 깃허브 로그인 -> 크롬 드라이버 103 오류 발생
        return True

# 로그인 함수
def login(id, pwd, github):
    # 소셜 로그인
    result = social_login(id, pwd, github)

    # 이메일 로그인
    if not result:
        # 프로그래머스 로그인 페이지로 이동
        programmers_login_page = 'https://programmers.co.kr/account/sign_in'
        driver.get(programmers_login_page)

        # 아이디 입력
        input_id = driver.find_element(by=By.XPATH, value='//*[@id="main-app-account"]/div/div[2]/div/div[2]/div[1]/div/div[2]/div[2]/input')
        input_id.send_keys(id)

        # 비밀번호 입력
        input_pwd = driver.find_element(by=By.XPATH, value='//*[@id="main-app-account"]/div/div[2]/div/div[2]/div[1]/div/div[2]/div[4]/input')
        input_pwd.send_keys(pwd)

        # 로그인 버튼 클릭
        button_login = driver.find_element(by=By.XPATH, value='//*[@id="main-app-account"]/div/div[2]/div/div[2]/div[1]/div/div[2]/button')
        button_login.send_keys(Keys.ENTER)
        driver.implicitly_wait(1)

    try:
        # 로그인 확인 = 로그아웃 버튼 확인
        driver.find_element(by=By.XPATH, value='//*[@id="main-app-root"]/div/div[1]/div[1]/div/div[2]/div/div[1]/div/div[1]/button')
    except:
        # 로그인 실패
        return 'Login Failed'

# 코드 제출 함수
def submit(problem, language, user_code):
    # 문제 url
    url = f'https://school.programmers.co.kr/learn/courses/30/lessons/{problem}?language={language}'
    driver.get(url)

    # 문제 존재 확인
    try:
        # 제출하기 버튼 확인 = 문제 존재 확인
        driver.find_element(by=By.XPATH, value='//*[@id="submit-code"]')
    except:
        # 문제가 존재하지 않는 경우
        return 'Problem Not Found'

    # 언어 존재 확인
    if driver.find_element(by=By.XPATH, value='//*[@id="tour7"]/button').text.lower() != language:
        return 'Language Not Found'

    # 코드 삽입을 위한 스크립트
    script = f'''
        // 사용자 코드
        const userCode = `{user_code}`;
        // 코드 에디터
        const editor = document.querySelector('.CodeMirror').CodeMirror;
        editor.getDoc().setValue(userCode); 
    '''

    # 코드 삽입 스크립트 실행
    driver.execute_script(script)

    # 코드 제출 button
    button_submit = driver.find_element(by=By.XPATH, value='//*[@id="submit-code"]')
    button_submit.send_keys(Keys.ENTER)

# 결과 출력 함수
def print_result():
    # 체점 완료될 때까지 대기
    while (True):
        try:
            # 채점 결과 modal
            driver.find_element(by=By.XPATH, value='//*[@id="modal-dialog"]/div')
            break
        except:
            driver.implicitly_wait(1)

    try:
        # 테스트 결과 컨테이너
        result_container = driver.find_element(by=By.XPATH, value='//*[@id="output"]/pre')
        print(result_container.text)
    except:
        # 테스트 실패(출력문 과다.. 등)
        test_failed = driver.find_element(by=By.CLASS_NAME, value='console-failed')
        print(test_failed.text)

# 입력 파일 내 사용자 풀이 코드를 반환하는 함수
def get_user_code():
    # 문제 파일 경로 (argv: 상대 경로 or 절대 경로)
    file = sys.argv[1]
    # 파일 열기
    file = open(file, 'r')
    # 파일 읽기
    user_code = "".join(file.readlines())
    
    return user_code

# 현재 터미널 내용을 지우는 함수
def clear():
    # 현재 os 확인
    OS = platform.system()

    # Windows
    if OS == 'Windows':
        os.system('cls')
    # Unix, Linux
    else:
        os.system('clear')

    if platform.system() == 'Windows':
        os.system()

# 프로그램 실행 함수
def main():
    # 문제 정보
    if len(sys.argv) != 4:
        print('index.py [문제 풀이 파일 경로] [문제 번호] [풀이 언어] 형식이 맞는지 확인해주세요.')
        return

    problem = sys.argv[2]
    language = sys.argv[3].lower()

    # .env 불러오기
    load_dotenv(verbose=True)

    # 사용자 정보 불러오기
    id = os.environ.get('ID')
    pwd = os.environ.get('PASSWORD')
    github = os.environ.get('GITHUB').lower() == 'true'

    # 현재 터미널 내용 지우기
    clear()

    # 로그인
    print('로그인 중...')
    error = login(id=id, pwd=pwd, github=github)
    if error == 'Login Failed':
        print(f'로그인 오류가 발생했습니다.')
        return

    # 사용자 코드
    user_code = get_user_code()

    # 현재 터미널 내용 지우기
    clear()

    # 문제 제출
    print('\n채점 중...')
    error = submit(problem=problem, language=language, user_code=user_code)

    if error == 'Problem Not Found':
        print(f'{problem}번 문제가 존재하지 않습니다.')
        return
    
    if error == 'Language Not Found':
        print(f'{problem}번 문제는 {language}를 지원하지 않습니다.')
        return

    # 현재 터미널 내용 지우기
    clear()

    # 결과 출력
    print_result()

# 드라이버 설정
driver = get_driver()

# 프로그램 실행
main()