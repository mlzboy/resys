1)执行exportdata___.py,使用exportdata___.py导出数据至exportdata/original/下
2)执行import2redis___.py,将exportdata/original下的文本，分词后的关键词导入redis的r0数据库中
3)执行wordcount____.py(注意这里是4个_,3个的那个其实是之前的版本，较之前多了一个position的sorted type),将相关的统计数据放入r1
4)执行脚本fillblank_matrix_data___.py生成空的matrix data
5)执行fill_real_matrix_data____.py(意这里是4个_,3个的那个是连外部数据库的版本)这个脚本生成访问6380端口的salve库
6)执行copy_slave_r2_to_master_r3___.py来从库填充的01矩阵复制到主库
7)执行calc_idf___.py计算r3矩阵的idf值，储存到r1中
8)执行calc_tfidf___.py计算基于r3计算tf/idf值后的矩阵到r4
9)执行prepare_message_queue___.py，将ro.keys()中的key的两两对，插入一个set中储存在r1中
执行clone_prepare_message_queue___.py在r1生成一个clone_queue队列，以便于在最后完成任务进行比对，看有哪些丢失的任务没有执行
10)执行generate_message_queue___.py,基于dreque生成工作任务集至r5,
11)多个脚本执行do_job___.py，将工作任务结果提交到r6中。
12)在将消息队列中的小任务都执行完成后，可能由于中途多次do_job___.py的执行，因此可能存在个别任务的丢失，
因此执行check_lost_tasks___.py来进行检测，并将找回的小任务，重新放入queue中
13)执行generate_lost_message_queue___.py为找回的未执行任务生成工作队列
14)再次使用do_job___.py来进行任务的执行
15执行export_similarity_result2csv___.py,export the data from redis memory to csv format
16)use the sqlserver commond tool bcp,execute bulk insert operator
bcp DMDM.dbo.similarities in f:\result.csv -c -t, -k -E -C936 -S10.3.10.90 -Uabc -Pabc
the similarities schema is as follows:
CREATE TABLE [dbo].[similarities](
	[p1] [varchar](20) NULL,
	[p2] [varchar](20) NULL,
	[sim] [float] NULL
) ON [PRIMARY]
17)执行query_similarity___.py来计算特定产品的topn推荐

注意：
1)在terimal中的编码，一般为gb18030格式，或是utf8格式，具体参看各脚本文件head部分的编码，与其一致
2)我们还使用了fill_real_matrix_data____checkisvalid.py来对fill_real_matrix_data____.py脚本生成的数据进行了比对
在进行这个测试的过程中，我们也使用了两个slave redis来同步一些原始的数据，使之对数据的操作不会影响
主库,主库用来生成原始的数据。
r0.dbsize当前为1801
r1.dbsize当前为5
r2.dbsize当前为1801
redis安装
git clone 

dreque的安装
sudo apt-get install git
sudo apt-get install git-core
sudo git clone git://github.com/samuel/dreque.git

redis-py的安装
sudo git clone git://github.com/andymccurdy/redis-py.git

将上述包安装完成后
再部署do_job___.py到多台ubuntu server上并行执行即可

关于表的说明
product表是到颜色的产品
Redundancy5颜色字段