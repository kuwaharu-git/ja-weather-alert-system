import requests
import xml.etree.ElementTree as ET
import re
import datetime

def main(code, municipalities):
    print(datetime.datetime.now())
    # データのURL
    url = "https://www.data.jma.go.jp/developer/xml/feed/extra.xml"
    res = requests.get(url)
    res.encoding = 'utf-8'
    root = ET.fromstring(res.text)

    # 名前空間の定義
    ns = {
        '': 'http://www.w3.org/2005/Atom',
    }

    # 'entry' 要素をすべて取り出す
    entries = root.findall('entry', ns)
    pattern = fr'_0_VPWW54_{code}\.xml'
    waring_name_list = []

    # 各entryのlinkを調べて特定の都道府県の一番新しいURLを取得する
    for entry in entries:
        link_attrib = entry.find('link', ns).attrib
        xml_url = link_attrib['href']
        
        if re.search(pattern, xml_url):
            print(f"Fetching data from URL: {xml_url}")
            res = requests.get(xml_url)
            res.encoding = 'utf-8'
            root = ET.fromstring(res.text)
            
            # Body要素を取得するための名前空間
            body_ns = {'jmx_body': 'http://xml.kishou.go.jp/jmaxml1/body/meteorology1/'}
            body = root.find('jmx_body:Body', body_ns)
            
            if body is not None:
                warnings = body.findall('jmx_body:Warning', body_ns)
                for warning in warnings:
                    if warning.get('type') == "気象警報・注意報（市町村等）":
                        # print("気象警報・注意報（市町村等）が見つかりました")
                        items = warning.findall('jmx_body:Item', body_ns)
                        for item in items:
                            area_name = item.find("jmx_body:Area/jmx_body:Name", body_ns)
                            # print(area_name.text)
                            if area_name is not None and area_name.text == municipalities:
                                kinds = item.findall("jmx_body:Kind", body_ns)
                                
                                for kind in kinds:
                                    name_elem = kind.find("jmx_body:Name", body_ns)
                                    status = kind.find("jmx_body:Status", body_ns)
                                    if not status.text == "解除":
                                        waring_name_list.append(name_elem.text)
                                print(f"警報情報: {waring_name_list}")
                                break
                        break
            else:
                print("Body 要素が見つかりませんでした")
            break
    else:
        print("現在該当の都道府県には警報はでていません")
    return waring_name_list


if __name__ == '__main__':
    main(130000, '新宿区')
