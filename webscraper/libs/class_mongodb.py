# coding=UTF-8

# --------------------------------------------------------------
# class_mongodb文件
# @class: MongoDB类
# @introduction: MongoDB类用来链接Mongodb数据库
# @dependency: pymongo包
# @author: plutoese
# @date: 2016.01.27
# --------------------------------------------------------------

from pymongo import MongoClient


class MongoDB:
    """MongoDB类连接MongoDB数据库进行操作

    :param str host: 数据库主机，默认是'localhost'
    :param int port: 数据库端口，默认是27017
    :return: 无返回值
    """
    def __init__(self, host='localhost', port=27017,mongo_str=None):
        # Client for a MongoDB instance
        # The clent object is thread-safe and has connection-pooling built in.
        if mongo_str is not None:
            self.__client = MongoClient(mongo_str)
        else:
            self.__client = MongoClient(host, port)
        #
        self.__db = None
        self.__collection = None

    def connect(self, database_name, collection_name=None):
        """连接MongoDB数据中的集合

        :param str database_name: 数据库名称
        :param str collection_name: 集合名称
        :return: 数据集合的连接
        :rtype: pymongo.collection.Collection对象
        """
        if database_name in self.__client.database_names():
            self.__db = self.__client[database_name]
        else:
            print('No such database: ', database_name)
            raise NameError

        if collection_name is not None:
            if collection_name in self.__db.collection_names():
                self.__collection = self.__db[collection_name]
            else:
                print('No such collection: ', collection_name)
                raise NameError

    def close(self):
        """ 关闭MongoDB连接

        :return: 无返回值
        """
        self.client.close()

    @property
    def client(self):
        """ 一个MongoDB实例的客户端

        :return: 返回一个MongoDB实例的客户端
        :rtype: pymongo.mong_client.MongoClient对象
        """
        return self.__client

    @property
    def database(self):
        """ MongoDB中的数据库

        :return: 返回某个MongoDB中的数据库
        :rtype: pymongo.database.Database对象
        """
        return self.__db

    @property
    def collection(self):
        """ MongoDB数据库中的集合

        :return: 返回MongoDB数据库中的某集合
        :rtype: pymongo.collection.Collection对象
        """
        return self.__collection

if __name__ == '__main__':
    db = MongoDB(mongo_str='mongodb://plutoese:z1Yh29@139.196.189.191:3717/')
    #db = MongoDB()
    print(db.client.database_names())
    #db.connect('region','province')
    #print(db.collection)

