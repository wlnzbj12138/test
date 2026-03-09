import pymysql
# 伪装版本 + 强制 utf8mb4 编码
pymysql.version_info = (2, 2, 1, "final", 0)
pymysql.charset = 'utf8mb4'
pymysql.install_as_MySQLdb()