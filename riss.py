import requests
from bs4 import BeautifulSoup
import furl
import time
import sys
import csv

search_keyword = input("검색어: ")
output_filename = input("결과 파일 이름: ")
if len(output_filename) == 0:
    output_filename = "result"
output_filename += ".csv"

start_count = 0
result_count = 0

fieldnames = ['제목', '저자', '학술지명', '발행연도', 'DOI식별코드', '검색키워드']

f = open(output_filename, "w")
writer = csv.DictWriter(f, fieldnames=fieldnames)


# %EC%B2%AD%EC%86%8C%EB%85%84+%EB%B2%94%EC%A3%84
# request_url = f"https://www.riss.kr/search/Search.do?isDetailSearch=N&searchGubun=true&viewYn=OP&queryText=&strQuery={search_keyword}&exQuery=&exQueryText=&order=%2FDESC&onHanja=false&strSort=RANK&p_year1=&p_year2=&iStartCount={start_count}&orderBy=&mat_type=&mat_subtype=&fulltext_kind=&t_gubun=&learning_type=&ccl_code=&inside_outside=&fric_yn=&db_type=&image_yn=&gubun=&kdc=&ttsUseYn=&l_sub_code=&fsearchMethod=search&sflag=1&isFDetailSearch=N&pageNumber=1&resultKeyword={search_keyword}&fsearchSort=&fsearchOrder=&limiterList=&limiterListText=&facetList=&facetListText=&fsearchDB=&icate=re_a_kor&colName=re_a_kor&pageScale=10&isTab=Y&regnm=&dorg_storage=&language=&language_code=&clickKeyword=&relationKeyword=&query={search_keyword}"
request_url = "https://www.riss.kr/search/Search.do?isDetailSearch=N&searchGubun=true&viewYn=OP&queryText=&strQuery={}&exQuery=&exQueryText=&order=%2FDESC&onHanja=false&strSort=RANK&p_year1=&p_year2=&iStartCount={}&orderBy=&mat_type=&mat_subtype=&fulltext_kind=&t_gubun=&learning_type=&ccl_code=&inside_outside=&fric_yn=&db_type=&image_yn=&gubun=&kdc=&ttsUseYn=&l_sub_code=&fsearchMethod=search&sflag=1&isFDetailSearch=N&pageNumber=1&resultKeyword={}&fsearchSort=&fsearchOrder=&limiterList=&limiterListText=&facetList=&facetListText=&fsearchDB=&icate=re_a_kor&colName=re_a_kor&pageScale=10&isTab=Y&regnm=&dorg_storage=&language=&language_code=&clickKeyword=&relationKeyword=&query={}"


response = requests.get(request_url.format(search_keyword, start_count, search_keyword, search_keyword))

if response.status_code == 200:
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    num_result = soup.select_one('#divContent > div > div.rightContent.wd756 > div > div.searchBox > dl > dd > span > span').get_text()
    print(f'검색 결과 수: {num_result}')
    print("")

    while start_count < int(num_result):
        response = requests.get(request_url.format(search_keyword, start_count, search_keyword, search_keyword))
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')

        ul = soup.select_one('#divContent > div > div.rightContent.wd756 > div > div.srchResultW > div.srchResultListW')
        results = ul.select('ul > li > div.cont.ml60')
        for result in results:
            print(f"{result_count + 1}/{num_result}")
            doi_value = "NONE"
            title = result.select_one('p.title').get_text()
            author = result.select_one('p.etc > span.writer').get_text()
            publisher_name = result.select_one('p.etc > span.assigned').get_text()
            publish_year = result.select_one('p.etc > span:nth-child(3)').get_text()
            link = result.select_one('p.title > a')['href']
            detail_link = "https://www.riss.kr" + link
            final_link = furl.furl(detail_link)
            final_link.remove(['keyword'])
            final_link = str(final_link)
            # print(f'세부링크: {final_link}')
            detail_page_response = requests.get(final_link, headers={'referer': final_link})

            if detail_page_response.status_code == 200:
                detail_html = detail_page_response.text
                detail_soup = BeautifulSoup(detail_html, 'html.parser')
                detail_list = detail_soup.select('#thesisInfoDiv > div.infoDetail.on > div.infoDetailL > ul > li > div > p > a')
                for detail in detail_list:
                    if "dx.doi.org" in detail.get_text():
                        print(f"DOI식별코드: {detail.get_text()}")
                        doi_value = detail.get_text()
                        break
                

            # print(f'제목: {title}')
            # print(f'저자: {author}')
            # print(f'학술지명: {publisher_name}')
            # print(f'발행연도: {publish_year}')
            # print("")
            new_entry = {'제목':title, '저자':author, '학술지명':publisher_name, '발행연도':publish_year, 'DOI식별코드':doi_value, "검색키워드":search_keyword}
            writer.writerow(new_entry)
            result_count += 1
        start_count += 10

f.close()