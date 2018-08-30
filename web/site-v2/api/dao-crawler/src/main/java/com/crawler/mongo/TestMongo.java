package com.crawler.mongo;

import java.util.Set;

import org.junit.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.mongodb.core.MongoTemplate;
import org.springframework.data.mongodb.core.query.Criteria;
import org.springframework.data.mongodb.core.query.Query;

import com.mongodb.DB;
import com.mongodb.Mongo;

public class TestMongo {
	@Test
    public void testMongodb(){  
      try{     
            // 连接到 mongodb 服务  
             Mongo mongo = new Mongo("192.168.1.202", 27017);    
            //根据mongodb数据库的名称获取mongodb对象 ,  
             DB db = mongo.getDB( "test" );  
             Set<String> collectionNames = db.getCollectionNames();    
               // 打印出test中的集合    
              for (String name : collectionNames) {    
                    System.out.println("collectionName==="+name);    
              }    
    	  
               
          }catch(Exception e){  
             e.printStackTrace();  
          } 
    }
	
	@Autowired
	MongoTemplate mongoTemplate;
	
	public Object find(int source){  
        
        return mongoTemplate.findOne(new Query(Criteria.where("source").is(source)), null); 
           
    }  
	
}

