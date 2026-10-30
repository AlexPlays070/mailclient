import smtplib, imaplib, email, os, getpass
from email import policy
from email.message import EmailMessage

SMTP_HOST, IMAP_HOST = "smtp.gmail.com", "imap.gmail.com"
EMAIL = input("Почта: ")
PASSWORD = getpass.getpass("Пароль приложения: ")

def send():
    msg = EmailMessage()
    msg["From"], msg["To"] = EMAIL, input("Кому: ")
    msg["Subject"] = input("Тема: ")
    msg.set_content(input("Текст: "))
    path = input("Путь к файлу (Enter - без файла): ").strip()
    if path:
        with open(path, "rb") as f:
            msg.add_attachment(f.read(), maintype="application",
                               subtype="octet-stream",
                               filename=os.path.basename(path))
    with smtplib.SMTP_SSL(SMTP_HOST, 465) as s:
        s.login(EMAIL, PASSWORD)
        s.send_message(msg)
    print("Отправлено")


def show(msg):
    print("\nОт:", msg["From"], "\nТема:", msg["Subject"])
    body = msg.get_body(("plain",))
    print(body.get_content() if body else "(нет текста)")
    for a in msg.iter_attachments():
        name = a.get_filename()
        if name:
            os.makedirs("downloads", exist_ok=True)
            with open(os.path.join("downloads", os.path.basename(name)), "wb") as f:
                f.write(a.get_payload(decode=True))
            print("Файл сохранён: downloads/" + name)


def receive():
    with imaplib.IMAP4_SSL(IMAP_HOST) as m:
        m.login(EMAIL, PASSWORD)
        m.select("INBOX")
        ids = m.search(None, "ALL")[1][0].split()[-10:]  # последние 10 писем (измените при необходимости)
        msgs = [email.message_from_bytes(m.fetch(i, "(RFC822)")[1][0][1],
                                         policy=policy.default) for i in ids]
    for n, msg in enumerate(msgs, 1):
        print(n, "|", msg["From"], "|", msg["Subject"])
    while True:
        n = input("\nНомер письма (Enter - назад): ")
        if not n:
            break
        if n.isdigit() and 1 <= int(n) <= len(msgs):
            show(msgs[int(n) - 1])


while True:
    c = input("\n1 - отправить, 2 - получить, 0 - выход: ")
    if c == "1": send()
    elif c == "2": receive()
    elif c == "0": break
