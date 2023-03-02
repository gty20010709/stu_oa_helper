import asyncio
from playwright.async_api import async_playwright, BrowserType
from lxml import html as Html
from tinydb import TinyDB,Query
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from getConfig import acconut,password,receiver_list,smtp_server,smtp_port

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

async def get_html(url) -> str:
    """
    获取OA首页的源码
    """
    async with async_playwright() as p:
        browser: BrowserType = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)
        html = await page.content()
        await browser.close()
    return html


def extract_items(html) -> list:
    """
    每条（item）信息都包含 标题(title)、URL(page_url)、发布单位(author)、日期(date)
    此函数将每条信息组合为一个dict，
    并将多条dict组成的列表返回
    """

    # 从str建立一个xpath树
    tree = Html.fromstring(html)
    # 从树中提取包含所有条目的表格
    lines = tree.xpath("/html/body/div/form/table/tbody[1]/tr")
    items = []

    # 提取出单独的条目，跳过第一条（表头）
    for i,line in enumerate(lines):
        if i == 0:
            pass
        else:
            
            title = line.xpath("td[1]/a/@title")[0]
            page_url = "http://oa.stu.edu.cn" + line.xpath("td[1]/a/@href")[0]
            author = line.xpath("td[2]/text()")[0]
            date = line.xpath("td[3]/text()")[0]
            # print(author,date,page_url)
            item = {
                "title":title,
                "page_url":page_url,
                "author":author,
                "date":date
            }
            items.append(item)
    
    return items



def email_or_pass(item,db) -> list:
    """
    判断一个条目的新旧，
    如是旧条目，在控制台提示，并返回None；
    如果是新条目，则返回该条目以待进一步处理
    """
    
    page_url = item["page_url"]
    query = Query()
    query_result = db.search(query.page_url == page_url)
    if not query_result:
        # send email and save to db
        # print(query_result)
        # send_list.append(item)
        return item

    else:
        print("item already in db")
        return None
    



def send_email(to, subject, body,account,password):
    """
    发送邮件，
    这段代码完全是从ChatGPT哪里抄来的，便不添注释了（。。。）
    """

    # Create message container
    msg = MIMEMultipart()
    msg['From'] = account
    msg['To'] = ", ".join(to)
    msg['Subject'] = subject

    # Add body to email
    body = MIMEText(body, 'html')
    msg.attach(body)

    # Send email using SMTP
    with smtplib.SMTP(smtp_server, smtp_port) as smtp:
        smtp.starttls()
        # logging.debug(f"{acconut} - {password}")
        smtp.login(account,password)
        smtp.send_message(msg)

def build_page(wait_to_send_list):
    """
    将需要传达的条目组合进一个页面
    最终呈现一个无序列表
    """
    lis = ""
    for item in wait_to_send_list:
        # 展开条目
        title,page_url,author,date = item.values()
        li = f"""<li><a href="{page_url}">{title}</a>-{author}-{date}</li>"""
        lis += li
    page = "<ul>" + lis + "</ul>" + """<br><p style="color:#3cff00;">PS: 此邮件由自动化程序发出，请勿回复！</p>"""
    return page
    
def update_db(db,wait_to_send_list):
    """
    当一条新item被传达给目标后，需要将其添加到数据库
    同时，为了尽可能减小数据库的体积，
    添加一条新数据后，便删除一条最旧的item

    这里或许还可以用 collections 的 deque 实现，
    应该会更简单，
    待日后再尝试罢
    """
    query = Query()
    def remove_the_oldest():
        oldest_item = db.all()[0]
        logging.debug(f"""remove {oldest_item["title"]}""")
        # print(oldest_item)
        db.remove(query.page_url == oldest_item["page_url"])

    for item in wait_to_send_list:
        logging.debug(f"""insert {item["title"]}""")
        db.insert(item)
        remove_the_oldest()
    


def main():
    url = "http://oa.stu.edu.cn/csweb/list.jsp?pageindex=1"
    db = TinyDB("db.json")

    html = asyncio.run(get_html(url))
    items = extract_items(html)
    wait_to_send_list = []
    for item in items:
        filtered_item = email_or_pass(item,db)
        wait_to_send_list.append(filtered_item)
    
    wait_to_send_list = [ x for x in wait_to_send_list if x is not None]

    if wait_to_send_list:
        subject = "Auto OA Sender"
        body = build_page(wait_to_send_list)
        attachment_path = ""
        send_email(receiver_list, subject, body,acconut,password)
        update_db(db=db,wait_to_send_list=wait_to_send_list)
        print(f"send {len(wait_to_send_list)} info(s) to target email")

if __name__ == "__main__":
    logging.debug("Start Program")
    main()
    logging.debug("End Program")