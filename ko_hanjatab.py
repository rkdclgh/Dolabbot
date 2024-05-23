import pywikibot
import re

def process_page(page):
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

    # '== 한국어 ==' 문단이 있는지 확인합니다.
    korean_section_pattern = re.compile(r'^==\s*한국어\s*==', re.MULTILINE)
    korean_section_match = korean_section_pattern.search(text)

    if korean_section_match:
        # '== 한국어 ==' 문단이 존재하면 '== 한자 ==' 문단을 삭제합니다.
        text = re.sub(r'^==\s*한자\s*==.*?(?=^==|\Z)', '', text, flags=re.MULTILINE | re.DOTALL)
        
        # '== 한국어 ==' 문단 바로 아래에 '{{ko-hanjatab}}'를 추가합니다.
        insert_pos = korean_section_match.end()
        text = text[:insert_pos] + "\n{{{{ko-hanjatab}}}}\n" + text[insert_pos:]
    else:
        # '== 한국어 ==' 문단이 존재하지 않으면 '== 한자 ==' 문단을 '== 한국어 ==' 문단으로 변경합니다.
        text = re.sub(r'^==\s*한자\s*==', '== 한국어 ==', text, flags=re.MULTILINE)
        
        # '== 한국어 ==' 문단 바로 아래에 '{{ko-hanjatab}}'를 추가합니다.
        korean_section_pattern = re.compile(r'^==\s*한국어\s*==', re.MULTILINE)
        korean_section_match = korean_section_pattern.search(text)
        if korean_section_match:
            insert_pos = korean_section_match.end()
            text = text[:insert_pos] + "\n{{{{ko-hanjatab}}}}\n" + text[insert_pos:]

    # 수정된 내용을 저장합니다.
    page.text = text
    page.save("자동화된 편집: 한자 활용 틀을 삭제하고 참고 틀을 추가함")

# 봇을 실행할 사이트를 설정합니다.
site = pywikibot.Site('ko', 'wiktionary')

# 대상 문서를 직접 지정하여 테스트합니다.
page = pywikibot.Page(site, '韓國語')
process_page(page)

# # '틀:한자 활용'을 사용하는 모든 문서를 가져옵니다.
# template_page = pywikibot.Page(site, '틀:한자 활용')
# referring_pages = template_page.getReferences(namespaces=0)

# # 각 문서를 처리합니다.
# for page in referring_pages:
#     process_page(page)
