import logging
from logging import handlers


class ThisLogger(object):
    level_relations = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL
    }

    # 默认的日志文件为 logging.log，默认等级为 info
    def __init__(self, filename='logging.log', level='info', when='D', backup_count=3,
                 formatter_str='[%(asctime)s] %(pathname)s %(module)s:%(lineno)d行: %(message)s'):
        self.logger = logging.getLogger(filename)

        self.logger.setLevel(self.level_relations.get(level))

        formatter = logging.Formatter(formatter_str)

        # 往屏幕上输出
        sh = logging.StreamHandler()
        # 设置屏幕上显示的格式
        sh.setFormatter(formatter)

        # 往文件里写入，并指定间隔时间自动生成文件
        th = handlers.TimedRotatingFileHandler(filename=filename, when=when, backupCount=backup_count,
                                               encoding='utf-8')
        # 实例化TimedRotatingFileHandler
        # interval是时间间隔，backup_count是备份文件的个数，如果超过这个个数，就会自动删除，when是间隔的时间单位，单位有以下几种：
        # S 秒
        # M 分
        # H 小时、
        # D 天、
        # W 每星期（interval==0时代表星期一）
        # midnight 每天凌晨
        th.setFormatter(formatter)

        self.logger.addHandler(sh)
        self.logger.addHandler(th)


# 测试本 logging 的日志等级和输出效果
def test():
    log = ThisLogger(level='debug')
    log.logger.debug('debug')
    log.logger.info('info')
    log.logger.warning('警告')
    log.logger.error('报错')
    log.logger.critical('严重')

    ThisLogger('error.log', level='error').logger.error('error')


if __name__ == '__main__':
    test()
