import pywikibot
import re
import csv
from datetime import datetime

def process_page(page, csv_writer):
    # 페이지 내용을 가져옵니다.
    text = page.text

    # '틀:한자 활용'을 찾습니다.
    hanja_pattern = re.compile(r'\{\{한자 활용.*?\}\}', re.DOTALL)
    hanja_template_match = hanja_pattern.search(text)

    if not hanja_template_match:
        return

    hanja_template = hanja_template_match.group(0)

    # '간체' 인수 값을 찾습니다.
    simplified_pattern = re.compile(r'\|?\s*간체\s*=\s*(.*?)\s*(?=\||\}\})')
    simplified_match = simplified_pattern.search(hanja_template)

    simplified_value = simplified_match.group(1).strip() if simplified_match else None

    # '틀:한자 활용'을 삭제합니다.
    text = hanja_pattern.sub('', text)

    # 문서 최상단에 '틀: 참고'를 추가합니다.
    if simplified_value:
        text = "{{{{참고|{}}}}}\n{}".format(simplified_value, text)

    # '== 한자 ==' 문단이 있는지 확인합니다.
    hanja_section_pattern = re.compile(r'^==\s*한자\s*==', re.MULTILINE)
    hanja_section_match = hanja_section_pattern.search(text)

    if hanja_section_match:
        # '== 한자 ==' 문단이 존재하면 해당 문단의 내용을 저장합니다.
        hanja_section_start = hanja_section_match.start()
        next_section_match = re.search(r'^==[^=]+==', text[hanja_section_start+1:], re.MULTILINE)
        hanja_section_end = next_section_match.start() + hanja_section_start + 1 if next_section_match else len(text)
        hanja_section_text = text[hanja_section_start:hanja_section_end].strip()

        # '== 한자 ==' 문단과 하위 내용을 삭제합니다.
        text = text[:hanja_section_start].strip() + "\n" + text[hanja_section_end:].strip()

        # '== 한자 ==' 문단 헤더를 삭제합니다.
        hanja_section_text = re.sub(r'^==\s*한자\s*==\n?', '', hanja_section_text).strip()

    else:
        hanja_section_text = ''

    # '== 한국어 ==' 문단이 있는지 확인합니다.
    korean_section_pattern = re.compile(r'^==\s*한국어\s*==', re.MULTILINE)
    korean_section_match = korean_section_pattern.search(text)

    if korean_section_match:
        insert_pos = korean_section_match.end()
        # 한국어 문단 바로 밑에 '{{ko-hanjatab}}'와 한자 문단 내용을 추가합니다.
        text = text[:insert_pos] + "\n{{ko-hanjatab}}\n" + hanja_section_text + "\n" + text[insert_pos:]
    else:
        # '== 한국어 ==' 문단이 없으면 '== 한자 ==' 문단을 '== 한국어 ==' 문단으로 변경하고, 내용을 추가합니다.
        text = '== 한국어 ==\n{{ko-hanjatab}}\n' + hanja_section_text + "\n" + text

    # 수정된 내용을 저장합니다.
    page.text = text
    page.save("자동화된 편집: 한자 문단을 한국어 문단으로 이동 및 ko-hanjatab 추가")

    # CSV 파일에 수정한 문서 정보를 기록합니다.
    csv_writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), page.title()])

# 봇을 실행할 사이트를 설정합니다.
site = pywikibot.Site('ko', 'wiktionary')

# CSV 파일을 엽니다.
csv_file_path = "edit_log_{}.csv".format(datetime.now().strftime("%y%m%d%H%M%S"))
with open(csv_file_path, mode='w', newline='', encoding='utf-8') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(['Timestamp', 'Page Title'])

    # '틀:한자 활용'을 사용하는 모든 문서를 가져옵니다.
    template_page = pywikibot.Page(site, '틀:한자 활용')
    referring_pages = template_page.getReferences(namespaces=0)

    # 각 문서를 처리합니다.
    for page in referring_pages:
        process_page(page, csv_writer)
