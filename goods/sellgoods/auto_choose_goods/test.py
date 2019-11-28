import smtplib
from email.mime.text import MIMEText

class SendEmail():

    def __init__(self, mail_account, passwd, recv, title, content, mail_host):
        """
       :param mail_account: 邮箱账号 xx@163.com
        :param passwd: 163的话是邮箱密码，qq的话是授权码
        :param recv: 邮箱接收人地址，多个账号以逗号隔开
        :param title: 邮件标题
        :param content: 邮件内容
        :param mail_host: 邮箱服务器，填163或qq
        """
        self.mail_account = mail_account
        self.passwd = passwd
        self.recv = recv
        self.title = title
        self.content = content
        self.mail_host = mail_host

    def send_mail(self, mail_account, passwd, recv, title, content, mail_host='smtp.163.com', port=25):
        # def send_mail(username, passwd, recv, title, content, mail_host='smtp.qq.com', port=465):
        '''
        发送邮件函数，默认使用163smtp
        :param mail_account: 邮箱账号 xx@163.com
        :param passwd: 163的话是邮箱密码，qq的话是授权码
        :param recv: 邮箱接收人地址，多个账号以逗号隔开
        :param title: 邮件标题
        :param content: 邮件内容
        :param mail_host: 邮箱服务器
        :return:
        '''
        msg = MIMEText(content)  # 邮件内容
        msg['Subject'] = title  # 邮件主题
        msg['From'] = mail_account  # 发送者账号
        msg['To'] = recv  # 接收者账号列表
        if self.mail_host:
            pass
        smtp = smtplib.SMTP_SSL(mail_host, port=port)  # 连接邮箱，传入邮箱地址，和端口号，smtp的端口号是25
        smtp.login(mail_account, passwd)  # 发送者的邮箱账号，密码
        smtp.sendmail(mail_account, recv, msg.as_string())
        # 参数分别是发送者，接收者，第三个是把上面的发送邮件的内容变成字符串
        smtp.quit()  # 发送完毕后退出smtp
        print('email send success.')



if __name__ == '__main__':
    # shelf_gap_expand_gooods('1')
    # a = goods_sort('0502')
    # print(a)

    email_user = 'wlgcxy2012@163.com'  # 发送者账号
    # email_user = '1027342194@qq.com'  # 发送者账号
    email_pwd = '2012wl'  # 发送者密码
    # email_pwd = 'rwpgeglecgribeei'  # 发送者密码
    maillist = '1027342194@qq.com'
    # maillist = 'wlgcxy2012@163.com'
    title = '测试邮件标题,haha111'
    content = '这里是邮件内容'
    # send_mail(email_user, email_pwd, maillist, title, content)