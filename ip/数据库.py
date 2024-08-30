import pymssql

server = 'sqlip.database.windows.net'
database = 'sqlip'
username = 'hotdog'
password = 'Cp1165750680'  # 注意：实际应用中应避免硬编码密码

# 创建连接
conn = pymssql.connect(server, username, password, database)
cursor = conn.cursor()

def insert_ip_addresses(ip_list):
    """
    将多个 IP 地址插入到 IPAddresses 表中。
    
    参数:
    ip_list -- 要插入的 IP 地址列表。
    """
    # 准备 SQL 插入语句
    insert_stmt = "INSERT INTO IPAddresses (IPAddress) VALUES (%s)"
    
    # 将 IP 地址列表转换为元组列表，以符合 executemany 的要求
    ip_data = [(ip,) for ip in ip_list]
    
    try:
        # 使用 executemany 批量插入 IP 地址
        cursor.executemany(insert_stmt, ip_data)
        # 提交事务
        conn.commit()
        print(f"{len(ip_list)} 条 IP 地址已成功插入到 IPAddresses 表中。")
    except pymssql.Error as e:
        # 回滚事务
        conn.rollback()
        print("插入 IP 地址时发生错误:", e)

# # 示例使用
# ip_addresses = ['192.168.1.1', '10.0.0.1', '172.16.0.1']
# insert_ip_addresses(ip_addresses)


def create_ip_addresses_table():
    """
    在数据库中创建 IPAddresses 表，如果表已存在则不创建。
    """
    create_table_stmt = """
    IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'IPAddresses')
    BEGIN
        CREATE TABLE IPAddresses (
            ID INT IDENTITY(1,1) PRIMARY KEY,
            IPAddress VARCHAR(15) NOT NULL
        );
    END
    """
    
    try:
        # 执行创建表的 SQL 语句
        cursor.execute(create_table_stmt)
        # 提交事务
        conn.commit()
        print("IPAddresses 表已成功创建或已存在。")
    except pymssql.Error as e:
        # 回滚事务
        conn.rollback()
        print("创建 IPAddresses 表时发生错误:", e)
# 调用函数创建表
create_ip_addresses_table()