package com.tsb.service.crawler.test;

import java.util.Set;

import org.junit.Test;

import com.mongodb.DB;
import com.mongodb.Mongo;

public class TestMongodb extends BaseTest{
	@Test   
    public void testMongodb()  
    {  
      try{     
            // 连接到 mongodb 服务  
             Mongo mongo = new Mongo("192.168.1.202", 27017);    
            //根据mongodb数据库的名称获取mongodb对象 ,  
             DB db = mongo.getDB( "crawler_v2" );  
             Set<String> collectionNames = db.getCollectionNames();
            
               // 打印出test中的集合    
              for (String name : collectionNames) {    
                    System.out.println("collectionName==="+name);    
              }    
               
          }catch(Exception e){  
             e.printStackTrace();  
          }  
}
}
